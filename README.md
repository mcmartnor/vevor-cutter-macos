English | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | [Polski](README.pl.md) | [Čeština](README.cs.md) | [Norsk](README.no.md)

# VEVOR Vinyl Cutter macOS Driver — CH554_CDC / USB 0483:5750 / Inkcut

[![License](https://img.shields.io/github/license/mcmartnor/vevor-cutter-macos)](LICENSE)

**VEVOR cutter not detected or not working on Mac?** This free, open-source macOS USB transport connects VEVOR and Anhui Anyu vinyl cutters to [Inkcut](https://github.com/inkcut/inkcut) when they identify as `CH554_CDC` with USB ID `0483:5750`.

No SignCut subscription, no Windows VM. This is a user-space libusb/pyusb transport — not a kernel extension, nothing to disable in macOS security settings.

> **Match your device before installing**
>
> Run in Terminal:
>
> ```bash
> system_profiler SPUSBDataType | grep -B 1 -A 5 "CH554"
> ```
>
> (or check **Apple menu → About → System Report → USB**). This project targets cutters showing:
>
> - Product: `CH554_CDC`
> - Vendor ID: `0x0483` — Product ID: `0x5750`
>
> A matching USB identity is required, but compatibility is confirmed only for the tested-hardware table below. The same USB ID is used across many rebrands — **VEVOR** (KH/KI/KW/SK series), **ANAgraph**, **Arthur**, **Art Creation**, **Cutter Pros**, **GoldCut**, **HELITIN**, **JinKa**, **SAGA**, **Secabo**, **Seron**, **US Cutter** — but firmware may differ; reports welcome.

## Fix a VEVOR cutter not detected or not cutting on Mac

If you are searching for VEVOR vinyl cutter software for Mac, a CH554_CDC Mac driver, or how to use a VEVOR cutter (plotter) with Inkcut, you have probably hit one of these:

- Cutter shows up in the USB tree but **no serial port** (`/dev/cu.*`) appears — Inkcut has nothing to connect to
- Sending a job does nothing, or the carriage **moves once and freezes**
- Letters and shapes cut **on top of each other** (duplicated cuts)
- Works right after power-on, then **dies while idle** until the next power cycle
- Inkcut errors like `OSError: … is not opened`

On the tested device, these symptoms were caused by one or more of the USB initialization, idle-suspend, protocol, and write-pacing behaviors described below. Other devices may fail for different reasons — see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## What we found (tested device; details in [docs/PROTOCOL.md](docs/PROTOCOL.md))

1. **A CDC serial port wearing a printer-class costume.** The firmware presents USB printer-class descriptors, but printer-class control requests STALL while CDC requests are accepted. The cutter buffers data without cutting until `SET_LINE_CODING` (9600 8N1) is sent and **DTR/RTS** are asserted via `SET_CONTROL_LINE_STATE`.
2. **The CH554 USB stack crashes when the idle port suspends.** A keep-alive (re-assert DTR/RTS every 15 s) prevents it; a USB port reset usually revives a wedged device without a power cycle.
3. **The native language is DMPL.** Init `;:H A L0 EC1 U`, tool up/down `U`/`D`, comma delimiter, space terminator, **0.025 mm/step** (1016 steps/inch). The HPGL mode half-works but wedged the firmware repeatedly in our testing. The firmware ignores DMPL `V` (velocity) commands — all pacing must happen host-side.
4. **The DMPL axes are transposed.** On this firmware the **first** coordinate drives the media feed rollers and the **second** the carriage — opposite of what Inkcut's device engine assumes. Compensating with Swap X/Y fixes the geometry but silently points Inkcut's feed logic (pre-feed, feed-past-cut, origin tracking) at the carriage. The transport ships a protocol-level `swap_axes` option (plus mirror) so the feed logic physically reaches the rollers.
5. **The internal buffer is tiny, and USB NAK is the only flow control.** The whole ring buffer holds a few hundred moves; large jobs overflow it mid-stream. pyusb (libusb) raises a bulk-write timeout **only when zero bytes were transferred** — a partially accepted transfer returns a short count — so retrying a timed-out chunk at the same offset is duplicate-safe. The transport uses exactly that as flow control: a dedicated writer thread retries while the cutter chews through its buffer, aborts only after 90 s with no progress, and a drain barrier keeps the job (and disconnect) from completing while data is still queued.

## What's in this repository

| Component | Description | Status |
|---|---|---|
| `inkcut-usb-transport/` | Native pyusb/libusb transport plugin for Inkcut: CDC init, DTR/RTS keep-alive, self-healing connect on a worker thread (auto USB reset + pipe probe before any cutting, GUI never freezes), queued writer thread with NAK-based flow control and duplicate-safe retries, drain barrier before job completion | Working on the tested device |
| `inkcut-pdf-import/` | **Open PDF and Adobe Illustrator (.ai) files directly in Inkcut** — converted off the UI thread on open (via poppler), with caching, drag-and-drop, multi-page warning, and the original file name kept in the UI/history | Working on the tested device |
| `inkcut-prefeed/` | **Material pre-feed**: slowly feeds the vinyl out to the job's full length and back before cutting, host-paced in small steps, so the roll never drags or slips mid-cut | Working on the tested device |
| Device profiles | VEVOR KH-870 / KH-720 driver entries (DMPL-first, USB, correct cutting widths 78/63 cm) with the `swap_axes`/mirror setup for the transposed firmware + feed-past-cut workflow (each job ends past the cut + 15 mm, ready for the next) | Working on the tested device |
| Inkcut UX patches | Graphic panel: editable **total layout size** when stepping up copies, Illustrator-style quick rotate buttons (90° left/right, 180°); app opens at a comfortable window size | Working on the tested device |
| `plotter_usb_bridge.py` | Standalone FIFO → USB daemon (launchd): anything that can write a file can drive the cutter | Working on the tested device |
| `patches/` | Unified diffs against upstream Inkcut for everything not shipped as a standalone component: pre-feed, flow-control integration, PDF/AI import integration, VEVOR profiles/axes, UX additions, raw-transport stale-connection fix | Available |
| [docs/PROTOCOL.md](docs/PROTOCOL.md) | Full USB + DMPL protocol notes and evidence for this cutter family | Available |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Symptom → cause → fix | Available |

Upstream status: not yet submitted to Inkcut.

## Installation status

> [!WARNING]
> **Pre-release.** There is no supported installer yet; the repository currently documents the protocol and the development transport. Watch [Releases](../../releases) for the first tested installation guide, and open an [Issue](../../issues) to volunteer a compatible device for testing.

## Tested hardware

| Model / rebrand | USB identity | macOS | CPU | Inkcut | Result |
|---|---|---|---|---|---|
| VEVOR KH-870 (D-type mainboard, 870 mm) | `0483:5750` / `CH554_CDC` | macOS 26.5 | Apple Silicon | 2.1.8 | Full workflow confirmed on vinyl via the native USB transport: PDF/AI import → pre-feed → cut with flow control → feed past cut, correct end position |

## Roadmap

- **Upstream to Inkcut**: bugfix PR (raw transport stale-connection) + the USB transport as a new connection type
- **More cutters**: community compatibility matrix — the transport's VID/PID/endpoint/baud are configurable, so other rebrands and chips can be tested and reported via Issues
- **Print-queue sharing**: a CUPS backend so *any* macOS app can print straight to the cutter as if it were a printer
- **Measure media width by jogging**: the firmware answers no position queries (probed), but the host tracks every absolute move — jog the head to the foil edge and one click sets the material width from the tracked position
- **Polished macOS app**: a signed Inkcut.app bundle with icon, so setup is drag-and-drop
- **Linux support**: the transport is pyusb and should work on Linux with udev rules; documentation planned

## Scope and alternatives

This project targets macOS cutters identifying as `CH554_CDC` / `0483:5750`. It does not claim compatibility with other VEVOR USB identities.

- **[Inkcut](https://github.com/inkcut/inkcut)** — the open-source cutting application this transport integrates with
- **SignCut Pro** — paid vendor-supported workflow for the same hardware
- **[vevor-cutter-linux](https://github.com/trifactoria/vevor-cutter-linux)**, **[VECTOCUT](https://github.com/MR-Lox/VECTOCUT)** — prior open-source work for related models/OSes; verify their supported USB identities separately

Research that helped map the terrain: [zi3.dev on the KW-780A](https://zi3.dev/vevor-kw-780a/), [abysm.org on 0483:5750 printer mode](https://blog.abysm.org/2021/03/vinyl-cutter-driver/).

## Support and contributing

Open a GitHub issue and include: exact cutter brand/model, USB vendor/product ID and product string, macOS version and CPU (Apple Silicon/Intel), Inkcut/Python versions, and relevant logs.
