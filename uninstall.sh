#!/bin/bash
# re.set — Uninstall script
PLIST="$HOME/Library/LaunchAgents/com.user.breakreminder.plist"
APP="$HOME/Applications/re.set.app"

echo "==> Stopping re.set …"
launchctl unload "$PLIST" 2>/dev/null || true
pkill -f "re\.set" 2>/dev/null || true
rm -f "$PLIST"

if [ -d "$APP" ]; then
    rm -rf "$APP"
    echo "==> Removed $APP"
fi

echo ""
echo "Uninstalled."
echo "User data in ~/Library/Application Support/re.set was NOT removed."
