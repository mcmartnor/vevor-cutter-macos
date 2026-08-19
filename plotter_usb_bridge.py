#!/usr/bin/env python
"""Relay bridge: FIFO -> Vevor plotter (USB printer-class, bulk OUT).

The Vevor cutter enumerates as a USB printer-class device (CH554_CDC,
0483:5750) so macOS creates no serial port for it, and modern macOS
removed raw CUPS queues. Inkcut therefore writes HPGL to a FIFO using
its "Raw device" transport, and this bridge forwards the bytes to the
plotter's bulk OUT endpoint via libusb.

The CH554 firmware crashes its USB stack when the port idles (macOS
suspends idle devices), leaving writes failing with EIO until a reset.
The bridge therefore keep-alive pings the device every 15s and attempts
a USB port reset before giving up on a failing write.

Run via launchd (com.inkcut.usbbridge) or manually:
    ~/.inkcut-venv/bin/python ~/.inkcut-venv/plotter_usb_bridge.py
"""
import os
import stat
import sys
import time
import errno
import struct
import threading

import usb.core
import usb.util

VID, PID = 0x0483, 0x5750
EP_OUT = 0x02
FIFO = os.path.expanduser("~/.inkcut-plotter")
CHUNK = 4096            # FIFO read size
USB_SLICE = 64          # max bytes per bulk transfer (endpoint packet size)
USB_TIMEOUT_MS = 5000   # per-slice bulk write timeout
MAX_ATTEMPTS = 5        # immediate-error retries per chunk before aborting
DEVICE_WAIT_S = 30      # total in-job wait for the device to (re)appear
KEEPALIVE_S = 15

# The firmware presents printer-class descriptors but actually implements
# CDC-ACM control requests (the product string is "CH554_CDC", and printer
# class requests STALL while CDC ones are accepted). Like SignCut's driver,
# assert the line coding and DTR/RTS or the firmware buffers data without
# executing it.
CDC_LINE_CODING = struct.pack('<IBBB', 9600, 0, 0, 8)  # 9600 8N1


def cdc_init(dev):
    dev.ctrl_transfer(0x21, 0x20, 0, 0, CDC_LINE_CODING, timeout=2000)
    dev.ctrl_transfer(0x21, 0x22, 0x03, 0, None, timeout=2000)  # DTR|RTS on

_lock = threading.Lock()   # serializes all USB access
_dev = None


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def _find_and_claim():
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        return None
    usb.util.claim_interface(dev, 0)
    cdc_init(dev)
    return dev


def get_device(wait=True, max_wait=None):
    """Find and claim the plotter. The lock is held only for the claim
    itself, never while sleeping, so the keepalive thread is never
    starved by a missing device. Returns None when not waiting or when
    max_wait seconds elapse without the device appearing."""
    global _dev
    announced = False
    start = time.monotonic()
    while True:
        with _lock:
            try:
                dev = _find_and_claim()
            except usb.core.USBError as e:
                log("claim failed (%s), retrying" % e)
                dev = None
            if dev is not None:
                log("plotter connected and claimed")
                _dev = dev
                return dev
        if not wait:
            return None
        if (max_wait is not None
                and time.monotonic() - start >= max_wait):
            return None
        if not announced:
            log("plotter not found on bus, waiting for it to appear")
            announced = True
        time.sleep(2)


def drop_device(reset=False):
    """Release the current handle; optionally try a USB port reset first
    (often revives the crashed CH554 without a physical power cycle)."""
    global _dev
    dev = _dev
    _dev = None
    if dev is None:
        return
    if reset:
        try:
            dev.reset()
            log("usb reset issued")
            time.sleep(2)
        except usb.core.USBError as e:
            log("usb reset failed (%s)" % e)
    try:
        usb.util.dispose_resources(dev)
    except Exception:
        pass


def keepalive():
    """Re-assert DTR/RTS periodically so macOS never suspends the port
    (the CH554 crashes on suspend). Never blocks on the lock: a busy lock
    means a write is in flight, which is already suspend-preventing
    traffic. On failure the handle is only marked dead; recovery belongs
    to the write path."""
    while True:
        time.sleep(KEEPALIVE_S)
        if not _lock.acquire(blocking=False):
            continue
        try:
            if _dev is None:
                continue
            try:
                _dev.ctrl_transfer(0x21, 0x22, 0x03, 0, None, timeout=2000)
            except usb.core.USBError as e:
                log("keepalive failed (%s), dropping handle" % e)
                drop_device(reset=False)
        finally:
            _lock.release()


def main():
    # A regular file at the FIFO path would be replayed endlessly by the
    # open/read loop (same cuts repeated forever) — insist on a FIFO.
    if os.path.lexists(FIFO) and not stat.S_ISFIFO(os.lstat(FIFO).st_mode):
        log("%s exists but is not a FIFO; replacing it" % FIFO)
        try:
            os.unlink(FIFO)
        except OSError as e:
            log("cannot remove %s (%s); refusing to run" % (FIFO, e))
            sys.exit(1)
    try:
        os.mkfifo(FIFO)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    log("fifo ready at %s" % FIFO)

    threading.Thread(target=keepalive, daemon=True).start()

    # Claim eagerly (if present) so keepalive protects the device before
    # the first job; don't block FIFO setup when the plotter is off.
    get_device(wait=False)

    while True:
        # Blocks until Inkcut opens the FIFO for writing.
        # buffering=0: a buffered read(4096) would block until a full
        # 4KB accumulates, stalling paced streams from Inkcut. Raw mode
        # returns whatever bytes are available immediately.
        with open(FIFO, "rb", buffering=0) as f:
            log("writer connected, job starting")
            total = 0
            abort = False
            wait_left = DEVICE_WAIT_S  # in-job device-wait budget
            while True:
                data = f.read(CHUNK)
                if not data:
                    break  # writer closed; reopen fifo
                if abort:
                    # Drain and discard the rest of this stream so the
                    # next job starts from a clean FIFO
                    continue
                total += len(data)
                # USB writes go out in endpoint-packet-size slices with
                # offset tracking: pyusb returns the bytes actually
                # transferred, and a partially-completed timeout comes
                # back as a SHORT COUNT rather than an exception, so
                # resuming from the offset never truncates or resends.
                offset = 0
                attempt = 0
                while offset < len(data):
                    with _lock:
                        have_dev = _dev is not None
                    if not have_dev:
                        waited_from = time.monotonic()
                        dev = get_device(max_wait=wait_left)
                        wait_left -= time.monotonic() - waited_from
                        if dev is None:
                            log("device did not return within the job "
                                "wait budget; ABORTING job")
                            abort = True
                            break
                    end = min(offset + USB_SLICE, len(data))
                    try:
                        with _lock:
                            if _dev is None:
                                # keepalive marked it dead in between
                                raise usb.core.USBError("device dropped")
                            n = _dev.write(EP_OUT,
                                           memoryview(data)[offset:end],
                                           timeout=USB_TIMEOUT_MS)
                        offset += n or 0
                    except usb.core.USBTimeoutError:
                        # Bytes may have been partially consumed; a resend
                        # would physically duplicate cuts. Abort the job.
                        log("write TIMED OUT mid-transfer; ABORTING job "
                            "to avoid duplicate cuts (power-cycle the "
                            "cutter and resend)")
                        with _lock:
                            drop_device(reset=True)
                        abort = True
                        break
                    except usb.core.USBError as e:
                        # Immediate failure: this slice was not consumed,
                        # retrying the same slice is safe — but bounded.
                        attempt += 1
                        if attempt >= MAX_ATTEMPTS:
                            log("write failed %d times (%s); ABORTING job"
                                % (attempt, e))
                            with _lock:
                                drop_device(reset=True)
                            abort = True
                            break
                        log("write failed (%s), attempt %d" % (e, attempt))
                        with _lock:
                            drop_device(reset=attempt >= 2)
                        time.sleep(1)
        if abort:
            log("job aborted after %d bytes; rest of stream discarded"
                % total)
        else:
            log("job done (%d bytes forwarded), waiting for next" % total)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
