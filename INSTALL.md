# re.set — Installation Guide (for friends)

> re.set is a macOS menu-bar app that reminds you to take breaks, log micro-workouts, and record focus sessions.  
> This guide is for people who received a ready-to-run `.app` file.

---

## System requirements

- macOS 12 Monterey or later
- Any Mac (Apple Silicon M1/M2/… or Intel)
- **No Python installation required** — the app is self-contained

---

## Install (one-time setup)

1. Unzip `re.set.zip` if you haven't already.
2. Drag **`re.set.app`** into your `/Applications` folder.
3. Double-click **`re.set`** in Applications.

The **leaf icon** will appear in the macOS menu bar — that's it.

### First launch: Gatekeeper warning

Because re.set is not signed by an Apple-registered developer, macOS may block it the first time:

**Option A (easiest):**
1. In Finder, **right-click** `re.set.app` → **Open**
2. A dialog asks "Are you sure you want to open it?" → click **Open**

**Option B (System Settings):**
1. Try to open the app normally — it will be blocked.
2. Go to **System Settings → Privacy & Security**
3. Scroll down — you'll see "re.set was blocked" → click **Open Anyway**

You only need to do this once.

---

## Auto-start at login (optional)

re.set does NOT auto-start by default when installed as a `.app`.  
To make it launch automatically when you log in:

1. Go to **System Settings → General → Login Items**
2. Click `+` → find `re.set.app` → click Open

---

## Usage

Once running, find re.set in the **menu bar** (top-right, leaf icon 🌿):

| Menu item | What it does |
|-----------|--------------|
| Timer (e.g. `下次休息：24:15`) | Time until next break |
| **暂停计时 / Pause Timer** | Pauses timer, locks screen |
| **回来了，记录一下 / I'm back** | Log what you did while away |
| **记录工作时段** | Manually log a focus session |
| **立即触发休息** | Trigger a break right now |
| **查看今日记录** | View today's records |
| **休息间隔** | Change interval (15–60 min) |
| **语言 / Language** | Switch Chinese ↔ English |
| **下班了 / End of Day** | Stop reminders, finalise score |
| **退出 / Quit** | Quit re.set |

### Emergency exit (if break window gets stuck)
Press **Shift + Ctrl + Option + Q**, then click once in the **bottom-left corner** of the screen.

---

## Your data

re.set stores all your personal data in:

```
~/Library/Application Support/re.set/
├── config.json                  ← preferences (interval, language)
├── activity_types.json          ← your custom activity types
├── break_reminder_state.json    ← today's score & check-ins
├── work_log.txt                 ← human-readable session log
└── history/                     ← per-day JSON archives
```

This folder is **never touched by app updates** — your history is safe.

---

## Uninstall

1. Quit re.set from the menu bar (退出 / Quit).
2. Remove the app:
   ```
   rm -rf /Applications/re.set.app
   ```
3. *(Optional)* Remove your personal data:
   ```
   rm -rf ~/Library/Application\ Support/re.set
   ```

---

## Troubleshooting

**App won't open / "damaged" message**  
Run this in Terminal, then try opening again:
```bash
xattr -cr /Applications/re.set.app
```

**Menu bar icon doesn't appear**  
Open Console.app and search for "re.set" to see error output.

**Port conflict (app already running)**  
```bash
lsof -ti tcp:18030 | xargs kill -9
```
Then re-open the app.
