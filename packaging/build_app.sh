#!/bin/bash
# packaging/build_app.sh — Build a self-contained re.set.app with py2app
#
# Usage (run from repo root):
#   bash packaging/build_app.sh
#
# Output:  dist/re.set.app   (ready to zip and distribute)
# Requires: Python 3.10+ in PATH (Homebrew or system, NOT /opt/homebrew hardcoded).
#           If py2app still fails on codesign, use Python 3.12 or 3.13 for the venv
#           (e.g. PYTHON=/opt/homebrew/bin/python3.12 bash packaging/build_app.sh).

set -e
REPO="$(cd "$(dirname "$0")/.."; pwd)"
cd "$REPO"

# ── 1. Locate Python (prefer explicit env var, then venv python, then PATH) ──
if   [ -n "$PYTHON" ] && command -v "$PYTHON" &>/dev/null; then
    PY="$PYTHON"
elif [ -f ".venv/bin/python3" ]; then
    PY="$REPO/.venv/bin/python3"
elif command -v python3 &>/dev/null; then
    PY="$(command -v python3)"
else
    echo "ERROR: python3 not found. Install Homebrew Python: brew install python" >&2
    exit 1
fi

echo "==> Using Python: $PY  ($($PY --version))"

# ── 2. Create / reuse venv ────────────────────────────────────────────────────
VENV="$REPO/.venv"
if [ ! -f "$VENV/bin/python3" ]; then
    echo "==> Creating venv at $VENV …"
    "$PY" -m venv "$VENV"
fi
source "$VENV/bin/activate"
echo "==> venv active: $(which python3)"

# ── 3. Install build deps ─────────────────────────────────────────────────────
echo "==> Installing py2app + PyObjC …"
pip install -q --upgrade pip wheel setuptools
pip install -q \
    py2app \
    pyobjc \
    pyobjc-core \
    pyobjc-framework-Cocoa \
    pyobjc-framework-WebKit \
    pyobjc-framework-Quartz

# ── 4. Clean previous build artefacts ────────────────────────────────────────
echo "==> Cleaning previous build …"
rm -rf build dist

# ── 5. Build ─────────────────────────────────────────────────────────────────
echo "==> Running py2app …"
python3 setup.py py2app 2>&1

if [ ! -d "dist/re.set.app" ]; then
    echo "ERROR: dist/re.set.app not found after build." >&2
    exit 1
fi

# ── 6. Clear quarantine + harden ad-hoc signature ────────────────────────────
echo "==> Clearing quarantine attributes …"
xattr -cr dist/re.set.app 2>/dev/null || true

echo "==> Re-signing all Mach-O binaries (ad-hoc) …"
find dist/re.set.app -type f | while read f; do
    if file "$f" 2>/dev/null | grep -qE 'Mach-O|dylib'; then
        /usr/bin/codesign --force --sign - "$f" 2>/dev/null || true
    fi
done
/usr/bin/codesign --force --deep --sign - dist/re.set.app 2>/dev/null || true

echo ""
echo "✅  Build succeeded: $REPO/dist/re.set.app"
echo ""
echo "Quick smoke test (Ctrl-C to stop after seeing menu bar icon):"
echo "  open dist/re.set.app"
echo ""
echo "To distribute, zip it:"
echo "  cd dist && zip -r re.set.zip re.set.app && echo Done"
