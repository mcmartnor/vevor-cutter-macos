# Troubleshooting — VEVOR / Anhui Anyu cutter on macOS

Symptom → likely cause → fix. All confirmed on a VEVOR KH-870 (`CH554_CDC`, `0483:5750`); other firmware may differ.

## No serial port (`/dev/cu.*`) ever appears
**Cause:** The cutter is a USB printer-class device; macOS does not create serial ports for it. This is normal for this hardware — nothing is broken.
**Fix:** Use a raw-USB path (this project's transport or bridge). Serial/CUPS-based instructions found online will not work on modern macOS.

## Data is "sent" but the cutter does nothing
**Cause 1:** No CDC init — the firmware buffers bytes but doesn't execute until `SET_LINE_CODING` (9600 8N1) + DTR/RTS are asserted.
**Fix:** Use a sender that performs the CDC init (this project does).
**Cause 2:** Another program holds the USB device (e.g. SignCut's spooler). Only one can claim the interface.
**Fix:** Quit the other program, retry.

## Carriage moves once, then freezes mid-job
**Cause:** Firmware wedge — seen with the HPGL mode and with unpaced streams; the buffer keeps ACKing while execution has stopped. The USB link may also drop entirely (device re-enumerates).
**Fix:** Power-cycle the cutter; switch to DMPL; make sure data is paced. If it recurs while idle, see the suspend item below.

## Shapes/letters cut on top of each other
**Cause:** Buffer overflow + blind retry: a timed-out bulk transfer was re-sent even though the cutter had consumed part of it.
**Fix:** Pace data at cutting speed; keep bulk writes small (≤64 B); never blindly retry a possibly-partial transfer.

## "Wedged pipe" / stall right at job start, but the cutter seems fine
**Cause:** The cutter is in **offline/origin-setting mode** on its front panel (e.g. you pressed offline to set the zero point and didn't confirm). In this mode it ACKs USB data into its buffer without executing — indistinguishable from a firmware wedge on the host side.
**Fix:** Confirm/exit the panel mode so the cutter is online, then resend. (The transport probes the pipe before cutting, so this is caught before any vinyl is wasted.)

## Works after power-on, dies after sitting idle
**Cause:** CH554 USB stack crashes when macOS suspends the idle port.
**Fix:** Keep-alive traffic every ~15 s while connected (re-assert DTR/RTS). A USB port reset usually revives it without power-cycling.

## Cutter is online but "swallows" a whole job silently
**Cause:** The plotter is in pause/offline, or a stale consumer read the stream, or the job went to a dead sink (e.g. `/dev/null` default path in Inkcut's raw transport).
**Fix:** Check the device path/transport configuration; verify the byte counts in whatever forwards data.

## Everything cuts, but 90° rotated
**Cause:** These cutters expect X along the feed direction.
**Fix:** In Inkcut: Device → Output → **Swap X/Y** (implemented as a true 90° rotation — no mirroring needed).

## Cut size is a few percent off
**Cause:** Steps-per-mm mismatch: D-type mainboards use 0.025 mm/step (1016/inch); some driver data floats 0.0254 (1000/inch); some software assumes 1021.
**Fix:** Cut a 100 mm test square and measure; set the resolution to match (see [PROTOCOL.md](PROTOCOL.md)).
