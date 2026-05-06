#!/bin/bash
# re.set — Uninstall script
PLIST="$HOME/Library/LaunchAgents/com.user.breakreminder.plist"

echo "==> Stopping re.set …"
launchctl unload "$PLIST" 2>/dev/null || true
pkill -f "break_reminder.py" 2>/dev/null || true
rm -f "$PLIST"

echo "Uninstalled. User data (history/, work_log.txt) was NOT removed."
