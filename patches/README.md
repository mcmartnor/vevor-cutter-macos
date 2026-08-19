# patches

Unified diffs against upstream Inkcut (generated vs. the master branch
at 2.1.9-dev, commit `c7a0c68`; they also apply to a 2.1.8 install —
the touched files are identical between the two).

## Applying

From the root of an Inkcut source tree (the directory containing
`inkcut/`):

```bash
patch -p1 < path/to/patches/<name>.patch
# or, in a git clone:
git apply path/to/patches/<name>.patch
```

Delete any `__enamlcache__`/`__pycache__` directories next to patched
`.enaml`/`.py` files afterwards, or a running install may keep using
stale compiled copies.

## What each patch does

| Patch | Feature area | Description |
|---|---|---|
| `core-utils.py.patch` | infrastructure | `defer_to_thread`: run blocking work on a daemon thread and deliver the result on the GUI thread via enaml `deferred_call` — Inkcut installs the twisted reactor but never starts it, so `deferToThread` must not be used |
| `device-plugin.py.patch` | prefeed, flow control | Pre-feed step generation (origin-relative, pause/cancel-able, velocity precedence), transport/protocol lists sorted by driver declaration, `flush()` drain barrier before job completion and disconnect, cancel handling during drain, precise transport errors surfaced to the user |
| `device-protocols-dmpl.py.patch` | axes | `DMPLConfig.swap_axes`: emit (y, x) for firmwares whose first DMPL coordinate drives the media feed (VEVOR/Anhui Anyu); corrected 1016 steps/inch resolution |
| `device-protocols-view.enaml.patch` | axes (UI) | "Swap axes" checkbox on the DMPL settings page |
| `device-drivers-manifest.enaml.patch` | driver profiles | VEVOR KH-870/KH-720 entries: DMPL-first, correct cutting widths (78/63 cm), `default_config` with `mirror_x` + `swap_axes` so fresh profiles work out of the box |
| `device-transports-raw-plugin.py.patch` | bugfix | Raw transport stale-connection/fd fix (device wedged after reconnect) |
| `job-plugin.py.patch` | PDF import | Open/convert PDF/AI off the UI thread, generation counter against stale conversions, drag-and-drop `can_open` for .pdf/.ai, multi-page warning dialog |
| `job-models.py.patch` | PDF import, prefeed | `source_document` (original path shown in UI/history), `final_size` (whole-layout size), feed-to-end inheritance, restore-time guards |
| `job-manifest.enaml.patch` | PDF import (UI) | File dialog filters for .pdf/.ai; dialog starts at the original document's directory |
| `job-view.enaml.patch` | UX | Graphic panel: editable total layout size when copies > 1, quick rotate buttons (90° left/right, 180°) |
| `ui-plugin.py.patch` | UX | Open the main window at double the default size, clamped to the screen |
