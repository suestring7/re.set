#!/bin/bash
# re.set — Install script
# Usage: bash install.sh
set -e

REPO_DIR="$(cd "$(dirname "$0")"; pwd)"
PYTHON="/opt/homebrew/bin/python3"
PLIST="$HOME/Library/LaunchAgents/com.user.breakreminder.plist"

echo "==> Checking Python 3 at $PYTHON …"
if ! command -v "$PYTHON" &>/dev/null; then
  echo "ERROR: Python 3 not found at $PYTHON."
  echo "  Install Homebrew first:  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
  echo "  Then install Python 3:   brew install python"
  exit 1
fi

PY_VERSION=$("$PYTHON" --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   Found Python $PY_VERSION"

echo "==> Installing PyObjC dependencies …"
"$PYTHON" -m pip install --quiet --break-system-packages \
  pyobjc-core \
  pyobjc-framework-Cocoa \
  pyobjc-framework-WebKit \
  pyobjc-framework-Quartz

echo "==> Making app bundle executable …"
chmod +x "$REPO_DIR/re.set.app/Contents/MacOS/re.set"

echo "==> Setting up LaunchAgent for auto-start …"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>             <string>com.user.breakreminder</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$REPO_DIR/break_reminder.py</string>
    </array>
    <key>WorkingDirectory</key>  <string>$REPO_DIR</string>
    <key>RunAtLoad</key>         <true/>
    <key>KeepAlive</key>         <true/>
    <key>ThrottleInterval</key>  <integer>10</integer>
    <key>StandardOutPath</key>   <string>$REPO_DIR/break_reminder.log</string>
    <key>StandardErrorPath</key> <string>$REPO_DIR/break_reminder.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo ""
echo "Installation complete!"
echo "re.set is running. Look for its icon in the macOS menu bar."
echo ""
echo "To start manually (without auto-start): double-click re.set.app"
echo "To uninstall: bash uninstall.sh"
