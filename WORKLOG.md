# re.set — Work Log

_Append a new entry here immediately after completing each step._

---

## 2026-05-15

### [1–7] Full feature batch (prior session)
- [1] Heatmap scroll: `renderHeatmap()` sets `scrollLeft=scrollWidth` after render
- [2] Exercise stars: `/api/exercise-stats` endpoint; hover panel shows count + star tier + progress bar fill
- [3] Timeline cards: work_content as primary (13px/600); exercise name demoted; score format fixed (`+-11` → `-11`)
- [4] Exercise form: `sets` + `duration_per_set` fields; saved to `user_exercises.json`
- [5] Pre-away tracking: `return_form.html` has "before you left" section; `_api_return_log` handles `before_leave`
- [6] Restroom analytics: big/small sub-chips; `event_type="restroom"`; `/api/restroom-stats`; "洗手间" tab in records_ui (gated by `menu_features.restroom_analytics`); Preferences toggle
- [7] Scheduled alerts: `AppConfig.scheduled_alerts`; `_check_scheduled_alerts()` per tick; `show_custom_alert` Observable; controller opens `custom_alert.html`; `/api/alerts` GET/POST; Preferences UI

### Alert save fix
- `saveAll()` in `preferences.html` now calls `await saveAlerts()` after `POST /api/prefs`, so the main Save button also persists alert changes

### Item 2 — Two logs on leave/return
- Added "before you left" section to the break window's inline away-return form (`break_reminder_ui.html` `v-away`)
- New chips (`#before-chips`), focus-minutes input (`#before-fm` pre-filled from `suggested_focus_minutes`), and work-content input (`#before-wc`)
- `renderBeforeChips()` renders ACT_TYPES chips for the before section
- `submitReturn()` now sends `before_leave: {activity_type, work_content, focus_minutes}` to `/api/return-log`
- Backend already handled `before_leave` in `_api_return_log` — no backend change needed here

### Item 3 — Warning panel position
- `controller.py` `showWarningPanel_`: changed `y = sh - ph - 20` (near top) to `y = sh * 0.35` (lower right, about 65% down the screen)

### Item 4a — 24h hover tooltip
- `records_ui.html`: `h24-block` elements now carry `data-act`, `data-wc`, `data-time`, `data-score`, `data-fm` attributes
- `onmouseenter` / `onmousemove` / `onmouseleave` on each block
- `showH24Tip()`, `posH24Tip()`, `hideH24Tip()` functions; `#h24-tooltip` div added to page
- Tooltip shows time range, activity dot + label, work content, focus min + score

### Item 4b — Timeline gap-fill
- `renderEvents()`: after rendering all cards, iterates pairs and inserts a `.ev-gap` button wherever gap ≥ 15 min between consecutive events
- `addGapRecord(prevTime, gapEnd)`: splices a phantom checkin (`_phantom:true`) into `curData.checkins`; opens in edit mode
- `saveEdit()`: detects phantom; routes to `POST /api/records/add` instead of `/api/records/edit`
- `cancelEdit()` / `deleteRecord()`: remove phantom from local array without API call
- New backend: `records_viewmodel.add_checkin()` + `_api_records_add` handler at `POST /api/records/add`

### Item 5 — Score away/return records
- `_api_return_log` in `http_server.py`: `away_checkin` score was hardcoded `1`; now uses `focus_score(fm, away_act)` where `away_act = self._lookup_act(act_id)`
- Same `focus_score` formula used for all regular check-ins; restroom returns `focus_score(fm, None)` = `fm/5`

**Files changed:** `platforms/macos/http_server.py`, `core/viewmodels/records_viewmodel.py`, `platforms/macos/controller.py`, `ui/break_reminder_ui.html`, `ui/records_ui.html`, `ui/preferences.html` (alert save fix from prior session)

**Rebuild required:** Python changes in `http_server.py`, `records_viewmodel.py`, `controller.py` require `bash packaging/build_app.sh`.

---

## 2026-05-17

### Bug fixes

**Restroom tab shows no data**
- Root cause: `_api_restroom_stats` did `records_vm.load_history_list() + [today]` — `load_history_list()` returns a `dict`, so `+` throws `TypeError`
- Fix: `hist = sorted(records_vm.load_history_list().keys())` then `all_dates = [d for d in hist if d != today] + [today]`

**Timeline gap-fill shows 时间块重叠**
- Root cause: `saveEdit` overlap check iterated `curData.checkins` (unsorted) and did `if(j===idx) continue` where `idx` is a sorted index — so it never skipped the phantom being edited. The phantom overlapped with itself.
- Fix: compute `_sortedCkins` and `_editedRec` BEFORE the overlap check; skip by reference (`ckins[j]===_editedRec`) and skip any other phantoms (`ckins[j]._phantom`)

**Away "before leave" default time included the away duration**
- Root cause: `showAwayReturn()` fetched `suggested_focus_minutes` at return time; by then `elapsed_minutes_since(last_checkin)` includes both work time + away time
- Fix `break_reminder_ui.html`: added `_beforeLeaveFm` variable; capture it in `initAwayView()` (at departure time, before away timer accumulates); use stored value in `showAwayReturn()`
- Fix `return_form.html`: same issue in the popup variant; changed pre-fill to `beforeFm = max(0, sug - awayMins)` where `sug` is total elapsed and `awayMins` is the away period

**Files changed:** `platforms/macos/http_server.py`, `ui/records_ui.html`, `ui/break_reminder_ui.html`, `ui/return_form.html`

**Rebuild required:** Python changes in `http_server.py`.

### Alert type enhancement

Added two new alert modes alongside the existing daily HH:MM mode:

- **每日 (daily):** fires every day at HH:MM — stored as `{type:'daily', time:'HH:MM'}`
- **指定时间 (once):** fires once at a specific date+time — stored as `{type:'once', fire_at:'YYYY-MM-DD HH:MM'}`
- **N分钟后 (relative):** fires once N minutes from now — client computes `fire_at = now + N*60s`, stored as `{type:'once', fire_at:computed}`

UI: `preferences.html` alert form now has a 3-button mode switcher (`af-mode-daily`, `af-mode-once`, `af-mode-rel`), each showing its own body section. `submitAlertForm()` builds the correct entry per mode. `_alertLabel(a)` renders: daily → `HH:MM`; once enabled → `MM-DD HH:MM` or `X分钟后`; once fired → `已触发`.

Backend: `_check_scheduled_alerts()` in `app_viewmodel.py` handles `"once"` type by comparing `datetime.now() >= datetime.strptime(fire_at, "%Y-%m-%d %H:%M")`; uses `_fired_once_ids` set for in-session deduplication; after firing sets `alert["enabled"] = False` and persists via `persistence.update_config(scheduled_alerts=...)`. `_api_alerts_post` in `http_server.py` validates and stores `fire_at` for `"once"` type, `time` for `"daily"` type.

**Files changed:** `ui/preferences.html`, `core/viewmodels/app_viewmodel.py`, `platforms/macos/http_server.py`

### Alert not triggering — timer loop fix

**Root cause:** The `_loop` in `BreakTimer` used `continue` inside `with self._lock:` for every skip condition (break_locked, away_mode, done_for_today, snooze, idle). `continue` exits the entire loop iteration, skipping `on_tick` at the bottom. So `_check_scheduled_alerts` (called from `_on_tick`) never ran when the app was in break/away/end-of-day/snooze state. Also caused snoozed breaks to never show the break window (snoozed_trigger was set but `on_break` was skipped by the same continue).

**Fix:** Replaced all `continue` statements inside the lock block with `if/elif/else` branches. `on_tick` now fires unconditionally every second regardless of timer state. Side effect: snoozed breaks now correctly call `on_break` when the snooze period expires.

**Files changed:** `core/timer/break_timer.py`

**Rebuild required:** `core/timer/break_timer.py`, `core/viewmodels/app_viewmodel.py`, `platforms/macos/http_server.py`, `platforms/macos/controller.py` (all from 2026-05-17 sessions).

---

## 2026-05-19

### Mood + feelings per check-in

Added optional mood and free-text note to every check-in record.

**Mood options** (5 emoji, stored as string id): `great`🤩, `good`😊, `okay`😐, `tired`😔, `stressed`😫. Tapping a selected mood de-selects it. Note is a plain text input, not required.

**Data model** (`core/models/checkin.py`): Added `mood: str | None = None` and `note: str = ""` fields; serialised only when non-empty.

**Backend:** `_api_checkin` and `_api_records_edit` in `http_server.py` pass `mood`/`note` through. `edit_checkin` and `add_checkin` in `records_viewmodel.py` apply the fields.

**Break form** (`break_reminder_ui.html`): Mood picker row (5 buttons) + note text input added between focus-time and the complete button. State `_mood` reset on each `goToCheckin()` call. Payload includes `mood` and `note`.

**Records timeline** (`records_ui.html`):
- Edit card: mood picker row + note input after work-content. `startEdit()` pre-populates `_editMood` from the record. `saveEdit()` sends `mood`/`note`. `cancelEdit()` clears `_editMood`.
- View card: mood emoji shown in the top row; note shown below work-content in muted italic.

**Files changed:** `core/models/checkin.py`, `core/viewmodels/records_viewmodel.py`, `platforms/macos/http_server.py`, `ui/break_reminder_ui.html`, `ui/records_ui.html`

**Rebuild required:** Python changes in `checkin.py`, `records_viewmodel.py`, `http_server.py`.
