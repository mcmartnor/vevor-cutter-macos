# inkcut-usb-transport

Native pyusb/libusb transport plugin for Inkcut, targeting cutters that
identify as `CH554_CDC` / USB `0483:5750` (VEVOR, Anhui Anyu and many
rebrands). It registers as an Inkcut connection type ("USB (libusb)")
via `manifest.enaml`.

What it does:

- CDC initialization (`SET_LINE_CODING` 9600 8N1 + DTR/RTS) even though
  the firmware presents printer-class descriptors
- DTR/RTS keep-alive so macOS never suspends the port (the CH554 USB
  stack crashes on suspend)
- Self-healing connect on a worker thread: automatic USB reset, reclaim
  and a 1-byte pipe probe before anything is cut — a wedged cutter is
  caught (or revived) before the job starts, and the GUI never freezes
- Queued writer thread with NAK-based flow control: a bulk-write
  timeout with zero bytes transferred is retried at the same offset
  (duplicate-safe per pyusb/libusb semantics), so the cutter's tiny
  ring buffer paces the host; aborts only after 90 s with no progress
- Drain barrier (`flush()`): a job is not reported complete, and the
  connection is not torn down, while data is still queued

Installation: copy this directory to
`inkcut/device/transports/usb/` in your Inkcut installation.

Dependencies:

- `pyusb` (`pip install pyusb`) and `libusb` (`brew install libusb`)
- the `defer_to_thread` helper and the flush/error integration in the
  device layer — apply `patches/core-utils.py.patch` and
  `patches/device-plugin.py.patch` from this repository (see
  `patches/README.md`)
