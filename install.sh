#!/bin/bash
# re.set — Install script
# Builds a self-contained app bundle and installs it to ~/Applications.
# Usage: bash install.sh
set -e

REPO_DIR="$(cd "$(dirname "$0")"; pwd)"
APP_DEST="$HOME/Applications/re.set.app"
PLIST="$HOME/Library/LaunchAgents/com.user.breakreminder.plist"

echo "==> Building re.set …"
bash "$REPO_DIR/packaging/build_app.sh"

echo "==> Installing to ~/Applications …"
mkdir -p "$HOME/Applications"
rm -rf "$APP_DEST"
cp -R "$REPO_DIR/dist/re.set.app" "$APP_DEST"

echo "==> Setting up LaunchAgent for auto-start …"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>             <string>com.user.breakreminder</string>
    <key>ProgramArguments</key>
    <array>
        <string>$APP_DEST/Contents/MacOS/re.set</string>
    </array>
    <key>RunAtLoad</key>         <true/>
    <key>KeepAlive</key>         <true/>
    <key>ThrottleInterval</key>  <integer>10</integer>
    <key>StandardOutPath</key>   <string>$HOME/Library/Logs/re.set.log</string>
    <key>StandardErrorPath</key> <string>$HOME/Library/Logs/re.set.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo ""
echo "Installation complete!"
echo "re.set is running — look for its icon in the menu bar."
echo ""
echo "To start manually:  open ~/Applications/re.set.app"
echo "To uninstall:       bash uninstall.sh"
