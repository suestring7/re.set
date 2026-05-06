# re.set — Break Reminder

A macOS break-reminder app that nudges you to step away from the screen, log a micro-workout, and record focus sessions — all from the menu bar.

---

## Features

- **Smart timer** — 30-minute countdown that only runs while you are actively using the computer (idle time pauses it).
- **Full-screen break overlay** — exercise cards, 20-second eye rest, focus-session log, and a completion check-in button.
- **Circuit training mode** — per-set countdown timer for each exercise, with visual progress dots.
- **Pause / away tracking** — click "暂停" (Pause) to lock the screen; when you return, log where you went (Restroom, Work, Life…).
- **End-of-day / Clock Out** — stops reminders and finalises the daily score.
- **Records panel** — day-by-day timeline, monthly heatmap, pie chart, and inline record editing.
- **Custom activity types** — user-defined labels and colours for work sessions.
- **Bilingual UI** — Chinese / English, switchable from the menu bar.

---

## Requirements

| Requirement | Version |
|---|---|
| macOS | 12 Monterey or later |
| Python | 3.10 or later (Homebrew recommended) |
| PyObjC | Installed by `install.sh` |

---

## Quick Install

```bash
git clone https://github.com/YOUR_USERNAME/re.set.git
cd re.set
bash install.sh
```

`install.sh` will:
1. Verify Python 3 is present at `/opt/homebrew/bin/python3`.
2. Install the four required PyObjC packages.
3. Make the app bundle executable.
4. Register a **LaunchAgent** so re.set starts automatically at login.

After running the script the app is live — look for the **leaf icon** in the macOS menu bar.

> **Python path note**: if your Python 3 lives somewhere other than `/opt/homebrew/bin/python3` (check with `which python3`), open `install.sh` and change the `PYTHON=` line before running.

---

## Manual Start (without auto-start)

Double-click **re.set.app** in the project folder.

Or from the terminal:

```bash
/opt/homebrew/bin/python3 break_reminder.py
```

---

## Uninstall

```bash
bash uninstall.sh
```

This removes the LaunchAgent and kills the running process. Your history and work logs are left untouched.

---

## File Overview

```
re.set/
├── break_reminder.py         # Backend: HTTP server, timer, macOS integration
├── break_reminder_ui.html    # Break overlay UI (full-screen)
├── records_ui.html           # Records panel (history, heatmap, pie chart)
├── away_form.html            # "Log Work Session" mini-form
├── return_form.html          # "I'm back" return-from-pause form
├── exercises.json            # Exercise library (37 exercises, circuit params)
├── re.set.app/               # macOS .app bundle for double-click launch
├── install.sh                # One-command installer
└── uninstall.sh              # Uninstaller
```

Files created at runtime (excluded from git):

```
history/                      # Per-day JSON archives
break_reminder_state.json     # Today's live state
activity_types.json           # Custom activity types
config.json                   # Interval and language prefs
work_log.txt                  # Human-readable session log
break_reminder.log            # App log
```

---

## Menu Bar Usage

| Item | Action |
|---|---|
| Timer (e.g. `下次休息：24:15`) | Shows time until next break |
| **暂停计时 / Pause Timer** | Locks screen, pauses timer |
| **回来了，记录一下 / I'm back** | Opens return form to log the away period |
| **记录工作时段** | Manually log a focus session |
| **立即触发休息** | Trigger a break right now |
| **查看今日记录** | Open the records panel |
| **休息间隔** | Change the interval (15 / 20 / 25 / 30 / 45 / 60 min) |
| **下班了 / End of Day** | Stop reminders and finalise score |
| **语言** | Switch Chinese ↔ English |
| **退出** | Quit re.set |

---

## Emergency Exit (hidden)

If the break window ever gets stuck: **Shift + Ctrl + Option + Q**, then click once in the **bottom-left corner** of the screen.

---

## Sharing with Others

1. Push this repo to GitHub (the `.gitignore` already excludes all personal data).
2. Share the repo URL.
3. Others clone and run `bash install.sh`.

No account, no server, no subscription — everything runs locally.

---

## License

MIT — do whatever you like with it.
