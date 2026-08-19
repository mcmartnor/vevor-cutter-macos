# Installation (macOS)

The quick way — three lines in Terminal:

```bash
git clone https://github.com/mcmartnor/vevor-cutter-macos.git
cd vevor-cutter-macos
./install.sh
```

The script installs nothing outside a Python virtualenv (default
`~/.inkcut-venv`) and never asks for sudo. Re-run any time with
`./install.sh --check` to verify the install and see whether the cutter
is visible on USB. Everything is pinned to the exact upstream Inkcut
commit and dependency versions the tested setup runs.

## What the script does (manual steps, if you prefer)

Prerequisites: [Homebrew](https://brew.sh).

```bash
# 1. System libraries: USB access, PDF conversion, Python
brew install libusb poppler python@3.12

# 2. A dedicated virtualenv
$(brew --prefix python@3.12)/bin/python3.12 -m venv ~/.inkcut-venv
~/.inkcut-venv/bin/pip install --upgrade pip

# 3. Inkcut, pinned to the commit the patches were made for,
#    plus the pinned dependencies
~/.inkcut-venv/bin/pip install \
    pyusb==1.3.1 qt-reactor==0.6.1 enaml==0.19.0 enamlx==0.6.4 PyQt5==5.15.11 \
    "inkcut @ git+https://github.com/inkcut/inkcut@c7a0c68980d03444f03bc019a3b4d82202efea32"

# 4. Apply this repository's patches to the installed package
SITE=~/.inkcut-venv/lib/python3.12/site-packages
for p in patches/*.patch; do patch -p1 -d "$SITE" < "$p"; done

# 5. Add the native USB transport and the PDF/AI importers
mkdir -p "$SITE/inkcut/device/transports/usb"
cp inkcut-usb-transport/*.py inkcut-usb-transport/*.enaml \
   "$SITE/inkcut/device/transports/usb/"
cp inkcut-pdf-import/importers.py "$SITE/inkcut/job/importers.py"

# 6. Start Inkcut
~/.inkcut-venv/bin/inkcut
```

## First run

1. **Device → Setup** and pick **VEVOR KH-870** or **KH-720**. The
   profile pre-configures DMPL mode 3, the transposed axes
   (`swap_axes`) and mirroring this firmware needs — a fresh profile
   cuts correctly out of the box.
2. Connection type: **USB (libusb)**. The cutter identifies as
   `CH554_CDC`, USB ID `0483:5750`; no serial port ever appears on
   macOS, and none is needed.
3. Cut something small. The job should end with the material fed 15 mm
   past the cut, ready for the next one.

## Known pitfalls

- **PDF/AI import fails** → poppler is missing:
  `brew install poppler`. Everything else works without it.
- **The cutter accepts the job but nothing moves** → the panel is in
  offline/origin mode. The firmware ACKs data without cutting in that
  state, which looks identical to a USB fault from the host side.
  Check the panel before debugging anything else.
- **Works after power-on, dies after sitting idle** → this is the
  firmware's idle-suspend crash. The transport's keep-alive prevents
  it while Inkcut is running; if the cutter was idle without Inkcut,
  power-cycle it once.
- More in [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Uninstall

Everything lives in the virtualenv:

```bash
rm -rf ~/.inkcut-venv
```

Inkcut's own settings live in `~/.config/inkcut/` — delete that too if
you want a completely clean slate.
