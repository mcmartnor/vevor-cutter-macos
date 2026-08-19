#!/bin/bash
# install.sh — VEVOR / Anhui Anyu vinyl cutter support for Inkcut on macOS
#
# Installs Inkcut (pinned upstream commit) into a Python virtualenv,
# applies this repository's patches, and adds the native USB transport
# and PDF/AI import. No sudo, nothing outside the venv is modified.
#
# Usage:
#   ./install.sh            install into ~/.inkcut-venv (refuses to overwrite)
#   ./install.sh --force    move an existing venv aside and reinstall
#   ./install.sh --check    verify an existing install and look for the cutter
#   INKCUT_VENV=/path ./install.sh   install somewhere else
set -euo pipefail

# Everything is pinned to the exact versions the tested setup runs
# (supply-chain hygiene: a moving dependency is an untested dependency).
INKCUT_COMMIT="c7a0c68980d03444f03bc019a3b4d82202efea32"
PINS=(
    "pyusb==1.3.1"        # bulk-timeout semantics the flow control relies on
    "qt-reactor==0.6.1"
    "enaml==0.19.0"
    "enamlx==0.6.4"
    "PyQt5==5.15.11"
)

VENV="${INKCUT_VENV:-$HOME/.inkcut-venv}"
REPO="$(cd "$(dirname "$0")" && pwd)"
MODE="${1:-install}"

say()  { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mWARNING:\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31mERROR:\033[0m %s\n' "$*" >&2; exit 1; }

site_dir() { "$VENV/bin/python" -c "import inkcut, os; print(os.path.dirname(os.path.dirname(inkcut.__file__)))"; }

check_install() {
    [ -x "$VENV/bin/python" ] || die "No install found at $VENV (set INKCUT_VENV or run ./install.sh first)"
    say "Checking install at $VENV"
    "$VENV/bin/python" - <<'PY'
import inkcut, usb.core
from inkcut.device.transports.usb import plugin as usb_transport
from inkcut.job import importers
from inkcut.core.utils import defer_to_thread
print("Inkcut import ......... OK (%s)" % inkcut.__file__)
print("USB transport ......... OK")
print("PDF/AI importers ...... OK")
devs = list(usb.core.find(find_all=True, idVendor=0x0483, idProduct=0x5750))
if devs:
    print("Cutter on USB ......... FOUND (0483:5750, %d device%s)"
          % (len(devs), "s" if len(devs) > 1 else ""))
else:
    print("Cutter on USB ......... not visible (plug it in and power it on)")
PY
    say "Check complete."
}

# ---------------------------------------------------------------- preflight
[ "$(uname)" = "Darwin" ] || die "This installer targets macOS."

if [ "$MODE" = "--check" ]; then check_install; exit 0; fi

command -v brew >/dev/null 2>&1 || die "Homebrew is required. Install it from https://brew.sh and re-run."

say "Checking Homebrew packages (libusb, poppler, python@3.12)"
for pkg in libusb python@3.12; do
    brew list --versions "$pkg" >/dev/null 2>&1 || brew install "$pkg"
done
if ! brew list --versions poppler >/dev/null 2>&1; then
    brew install poppler || warn "poppler could not be installed — PDF/AI import will be unavailable (everything else works). Retry later with: brew install poppler"
fi

PYTHON="$(brew --prefix python@3.12)/bin/python3.12"
[ -x "$PYTHON" ] || die "python3.12 not found at $PYTHON"

# ---------------------------------------------------------------- venv
if [ -e "$VENV" ]; then
    if [ "$MODE" = "--force" ]; then
        BACKUP="$VENV.old-$(date +%Y%m%d-%H%M%S)"
        say "Moving existing $VENV to $BACKUP"
        mv "$VENV" "$BACKUP"
    else
        die "$VENV already exists. Re-run with --force to move it aside and reinstall, or set INKCUT_VENV to another path."
    fi
fi

say "Creating virtualenv at $VENV"
"$PYTHON" -m venv "$VENV"
"$VENV/bin/pip" -q install --upgrade pip

say "Installing Inkcut (upstream @ ${INKCUT_COMMIT:0:7}) and pinned dependencies"
"$VENV/bin/pip" -q install "${PINS[@]}" \
    "inkcut @ git+https://github.com/inkcut/inkcut@$INKCUT_COMMIT"

SITE="$(site_dir)"
[ -d "$SITE/inkcut" ] || die "Could not locate installed inkcut package."

# ---------------------------------------------------------------- patches
say "Applying patches to $SITE/inkcut"
for p in "$REPO"/patches/*.patch; do
    patch -p1 -s -d "$SITE" < "$p" || die "Patch failed: $(basename "$p") — the pinned base should always match; please open an issue."
done

say "Installing the native USB transport and PDF/AI importers"
mkdir -p "$SITE/inkcut/device/transports/usb"
for f in "$REPO"/inkcut-usb-transport/*.py "$REPO"/inkcut-usb-transport/*.enaml; do
    cp "$f" "$SITE/inkcut/device/transports/usb/"
done
cp "$REPO/inkcut-pdf-import/importers.py" "$SITE/inkcut/job/importers.py"

# ---------------------------------------------------------------- verify
say "Verifying"
"$VENV/bin/python" -m py_compile \
    "$SITE/inkcut/device/plugin.py" \
    "$SITE/inkcut/device/transports/usb/plugin.py" \
    "$SITE/inkcut/device/protocols/dmpl.py" \
    "$SITE/inkcut/job/importers.py" \
    "$SITE/inkcut/job/plugin.py" \
    "$SITE/inkcut/core/utils.py"
"$VENV/bin/python" -c "import inkcut, usb" || die "Post-install import check failed."

say "Done!"
cat <<EOF

Next steps:
  1. Start Inkcut:            $VENV/bin/inkcut
  2. Add your cutter:         Device -> Setup -> select VEVOR KH-870 or KH-720
                              (the profile pre-configures the transposed DMPL
                              axes and mirroring this firmware needs)
  3. Connection type:         USB (libusb) — the cutter shows as CH554_CDC,
                              USB ID 0483:5750; no serial port is needed
  4. Verify the cutter:       $0 --check

If something misbehaves, see docs/TROUBLESHOOTING.md — and please report
your cutter model (working or not) in a GitHub issue.
EOF
