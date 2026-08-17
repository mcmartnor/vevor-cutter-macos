# USB and DMPL protocol notes — Anhui Anyu / VEVOR CH554 cutters

Everything below was reproduced on a VEVOR KH-870 (D-type mainboard) on macOS 26.5 / Apple Silicon, cross-checked against the manufacturer's driver definitions shipped with SignCut Pro 2 (`drivers.pak`: `vevor.xml`, `anhuianyu.xml`; `usb-devices.xml`). Other devices sharing the USB identity may differ.

## USB identity and descriptors

- VID `0x0483` (1155), PID `0x5750` (22352), product string `CH554_CDC` (WCH CH554 microcontroller with an STMicro VID)
- One configuration, one interface: class `0x07` (printer), subclass `0x01`, protocol `0x02` (bi-directional)
- Endpoints: `0x81` interrupt IN (8 B), `0x02` bulk OUT (64 B), `0x82` bulk IN (64 B)
- The same VID:PID is shared by at least 12 rebrands (SignCut's `usb-devices.xml`): ANHUIANYU, Arthur, Art Creation, Cutter Pros, GoldCut, HELITIN, JinKa, SAGA, Secabo, Seron, US Cutter, VEVOR

## The printer/CDC split personality

Despite printer-class descriptors:

| Request | Result |
|---|---|
| Printer-class `GET_PORT_STATUS` (0xA1, 0x01) | **STALL** |
| Printer-class `SOFT_RESET` (0x21, 0x02) | **STALL** |
| Printer-class `GET_DEVICE_ID` (0xA1, 0x00) | returns 1 junk byte |
| CDC `SET_LINE_CODING` (0x21, 0x20, 9600 8N1) | **accepted** |
| CDC `SET_CONTROL_LINE_STATE` (0x21, 0x22, DTR\|RTS) | **accepted** |

Without the CDC init, the firmware ACKs bulk data into its buffer but does not execute it. SignCut's own working configuration for this device (spooler `config.xml`) is `9600 8N1, DTR=1, RTS=1, CTS=1` over raw libusb bulk transfers (libusb is statically linked into their spooler; no serial tty is used).

Init sequence that works:

```
SET_LINE_CODING: bmRequestType 0x21, bRequest 0x20, data = <IBBB> 9600, 0, 0, 8
SET_CONTROL_LINE_STATE: bmRequestType 0x21, bRequest 0x22, wValue 0x0003 (DTR|RTS)
```

## Idle-suspend firmware crash

Left idle, the device drops off the bus or stops accepting bulk writes (`EIO` / timeouts) until reset. Root cause is consistent with the CH55x USB stack crashing on macOS's selective suspend. Mitigations that work on the tested device:

- Re-assert `SET_CONTROL_LINE_STATE` every 15 s while claimed (doubles as suspend-preventing traffic)
- On repeated write failure: `libusb` port reset (`dev.reset()`), wait ≥2 s for re-enumeration, re-claim, re-init CDC

## Native language: DMPL

From the manufacturer's driver definitions (and confirmed by cutting):

| Parameter | Value |
|---|---|
| Language | DMPL, absolute coordinates |
| Resolution | **0.025 mm/step** = 1016 steps/inch (KH-870 D-type; the `anhuianyu.xml` variant lists 0.0254) |
| Init | `;:H A L0 ECN U` (N = force preset, e.g. `EC1`) |
| Tool | `U` up, `D` down, format `U<x>,<y> ` / `D<x>,<y> ` |
| Delimiter / terminator | `,` / space (`0x20`) |
| After job | `@` |
| Default blade offset | 0.36 mm (KH-870) / 0.25 mm (anhuianyu variant) |
| Serial defaults | 9600 8N1 (D-type); A-type mainboards (KH-870A/KI-…A) are true HPGL at 38400 |

The firmware also has an HPGL mode (`IN;PU…;PD…;`) at 40 steps/mm which cuts, but in our testing it intermittently wedged the firmware mid-job (carriage stops after the first travel move; buffer keeps ACKing). DMPL is what the vendor software uses.

## Buffer behavior / pacing

The onboard buffer is small. Two failure modes when streaming too fast:

1. Bulk OUT stalls (NAK) → host timeout → if the transfer is blindly retried, already-consumed bytes are cut twice (physically overlapping cuts)
2. Long stalls wedge the firmware entirely

Safe operation: pace commands at cutting speed (Inkcut's device engine does this: per-command delay proportional to move distance), keep individual bulk writes ≤64 B, and never retry a possibly-partial transfer blindly.
