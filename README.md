# re.set — Break Reminder

A macOS menu-bar app that reminds you to take breaks, log micro-workouts, and track focus sessions — no account, no server, everything local.

---

## Features

- **Smart timer** — countdown that only runs while you're actively typing/clicking; idle time doesn't count.
- **Break overlay** — exercise cards, 20-second eye rest, focus-session log, and a check-in button.
- **Circuit training mode** — per-set countdown with visual progress dots and three exercise categories (stretch · core · strength).
- **Away tracking** — pause the timer when you step away; log where you went on return.
- **End-of-day / Clock Out** — stops reminders and finalises the daily score.
- **Records panel** — day timeline, monthly heatmap, 24-hour chart, bar chart, and inline record editing.
- **Custom activity types** — user-defined labels, colours, and focus-score weights.
- **Bilingual UI** — Chinese / English, switchable from the menu bar.

---

## Installation

### Option A — Pre-built app (recommended)

Download the latest DMG for your chip from the [Releases](../../releases) page:

| File | For |
|---|---|
| `re.set-vX.Y.Z-apple-silicon.dmg` | M1 / M2 / M3 / M4 Macs |
| `re.set-vX.Y.Z-intel.dmg` | Intel Macs |

Mount the DMG, drag **re.set.app** to `~/Applications` (or `/Applications`), then:

```
Right-click → Open
```
(Required once on first launch because the app is not notarized.)

### Option B — Build from source

**Requirements:** macOS 12+, Python 3.10+, pip

```bash
git clone https://github.com/suestring7/re.set.git
cd re.set
bash install.sh
```

`install.sh` builds a self-contained `.app` via py2app, copies it to `~/Applications`, and installs a **LaunchAgent** so re.set starts automatically at login.

After running, look for the leaf icon in the menu bar.

---

## Manual Start / Stop

```bash
# Start without auto-start
open ~/Applications/re.set.app

# Or run directly from source (no build needed)
python3 main_macos.py

# Uninstall (removes LaunchAgent, leaves your history intact)
bash uninstall.sh
```

---

## Menu Bar Reference

| Item | Action |
|---|---|
| `下次休息：24:15` | Time until next break (live countdown) |
| **暂停计时 / Pause Timer** | Pauses timer, opens away-tracking mode |
| **回来了，记录一下 / I'm back** | Log the away period on return |
| **记录工作时段** | Manually log a focus session |
| **立即触发休息** | Trigger a break right now |
| **查看今日记录** | Open the records panel |
| **休息间隔** | Change interval (15 / 20 / 25 / 30 / 45 / 60 min) |
| **下班了 / End of Day** | Stop reminders, finalise daily score |
| **语言** | Switch Chinese ↔ English |
| **退出** | Quit |

**Stuck break window?** Press **Shift + Ctrl + Option + Q**, then click the bottom-left corner of the screen.

---

## Project Structure

```
re.set/
├── core/                     # Pure Python — no OS imports, portable to any platform
│   ├── models/               # Exercise, CheckIn, DailyRecord, ActivityType, AppConfig
│   ├── services/             # PersistenceService, ExerciseService, scoring functions
│   ├── timer/                # BreakTimer (threading-based, PlatformAdapter protocol)
│   ├── utils/                # Observable[T], date helpers
│   └── viewmodels/           # AppViewModel, RecordsViewModel, PreferencesViewModel
│
├── platform/
│   ├── macos/                # MacOSAdapter (Quartz idle), controller, HTTP server
│   └── windows/              # Stub — future Windows port
│
├── ui/                       # HTML/JS UI served over localhost (shared across platforms)
│   ├── break_reminder_ui.html
│   ├── records_ui.html
│   ├── preferences.html
│   ├── away_form.html
│   ├── return_form.html
│   ├── warning.html
│   ├── shared.js
│   ├── exercises.json        # 37 exercises across stretch / core / strength
│   └── activity_types.json   # Default activity type definitions
│
├── tests/                    # Unit tests (pytest)
│   ├── test_scoring.py
│   └── test_exercise_service.py
│
├── main_macos.py             # Entry point (macOS)
├── break_reminder.py         # Original monolith — kept runnable during refactor
├── setup.py                  # py2app build config
├── install.sh                # Build + install to ~/Applications + LaunchAgent
└── uninstall.sh
```

Runtime files (excluded from git, stored in `~/Library/Application Support/re.set/`):

```
history/                      # Per-day JSON archives
break_reminder_state.json     # Today's live state
activity_types.json           # User's custom activity types
config.json                   # Interval and language prefs
work_log.txt                  # Human-readable daily log
```

---

## Building Releases

Releases are built automatically by GitHub Actions on every version tag:

```bash
git tag v1.2.0
git push origin v1.2.0
```

This builds both an Intel DMG and an Apple Silicon DMG in parallel and publishes them as assets on a GitHub Release. See [`.github/workflows/release.yml`](.github/workflows/release.yml).

---

## Running Tests

```bash
python -m pytest tests/
```

---

## Architecture

re.set uses a **Python MVVM** pattern designed for cross-platform portability:

- **`core/`** — pure Python, zero OS-specific imports. Runs identically on macOS and Windows.
- **`platform/macos/`** — thin adapter layer: Quartz idle detection, `NSStatusItem` menu bar, `WKWebView` windows.
- **`ui/`** — HTML/JS served over `localhost:18030` by an embedded HTTP server. No changes needed for other platforms.
- **`platform/windows/`** — stub for a future Windows port (pystray + `ctypes` idle + `webbrowser.open()`).

Dependency direction is strictly one-way: `platform/` → `core/`, never reversed.

---

## License

MIT — do whatever you like with it.
