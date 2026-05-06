# HACKING.md — re.set developer guide

Practical notes for extending and debugging **re.set** (macOS break reminder).

---

## Architecture overview

### Python process & threads

- **HTTP server thread** — `http.server` serves the WKWebView UI (`break_reminder_ui.html`, records, forms, `/api/*`).
- **Main thread / NSRunLoop** — PyObjC `NSApplication`, menu bar, native windows (`BreakWindow`, warning panel, prefs).
- **Idle timer thread** — polls Quartz idle time vs `IDLE_THRESHOLD`; drives “active seconds” accumulation.

### Pages (what each does)

| Route | File | Role |
|-------|------|------|
| `/` | `break_reminder_ui.html` | Break overlay: exercises, check-in, eye timer, activity types |
| `/records` | `records_ui.html` | Today/history, charts |
| `/away-form` | `away_form.html` | Log work session from menu |
| `/return-form` | `return_form.html` | “Welcome back” after away |
| `/preferences` | `preferences.html` | Interval, language, activity weights |
| `/warning` | `warning.html` | Small floating countdown before break |
| `/shared.js` | `shared.js` | Shared browser helpers (activity types, formatting, type manager widget) |

### State lifecycle

- **`_g`** — In-memory globals (timer, language mirror, away mode, etc.).
- **`break_reminder_state.json`** — Today’s score, check-ins, category counts (see `load_state` / `save_state`).
- **`config.json`** — User prefs (interval, language, …) via `load_config` / `save_config`.
- **`history/YYYY-MM-DD.json`** — Past days when rolled over.
- **`activity_types.json`** — Activity type definitions (labels, colors, **weights**).

Static tunables and extra fields exposed to the browser live under **`GET /api/config`** (merged with `load_config()`): `daily_minimums`, `eye_timer_seconds`, `warning_advance_seconds`, `idle_threshold_seconds`.

---

## How to add a new exercise

1. Edit **`exercises.json`** — each exercise needs whatever schema the backend expects (id, title, category, score, … — keep in sync with `pick_exercises()` and check-in handling).
2. **`pick_exercises()`** (in `break_reminder.py`) chooses the three cards shown; adjust filters/priority there.
3. **`DAILY_MINIMUMS`** — per-category minimum counts; affects progress UI and “all minimums met”. Defined as a tunable constant in `break_reminder.py` and exposed via `/api/config` as `daily_minimums`.

---

## How to add a new activity type

1. **UI** — `/preferences` (weights) or inline type manager on break / away forms (posts to `/api/activity-types`).
2. **File** — Edit **`activity_types.json`** directly if needed (same shape as API: `id`, `label`, `color`, `weight`).
3. **Scoring** — Focus points use `floor(minutes × weight / 5)` server-side (`activity_focus_score_points()`); client preview uses the same weight in `updateScoreEst()` on the break UI.

---

## How to add a new API endpoint

1. Register in **`do_GET`** or **`do_POST`** on `Handler` — map path → method.
2. Implement **`_api_foo(self)`** on `Handler`.
3. **Read body** — `data = self._body()` (JSON).
4. **Respond** — `self._json({...})` or `self._html(bytes_or_str)`.

---

## How to add a new UI page

1. Add **`something.html`** next to the other HTML files.
2. Add **`_serve_something`** that reads the file like `_serve_records`.
3. Register **`/something`** in **`do_GET`**.
4. To open in a new native window, follow the pattern used for preferences (`showPreferences_:` / similar `NSWindow` + `WKWebView`).

---

## How to change scoring

- **Backend** — `activity_focus_score_points()` in `break_reminder.py`.
- **Weights** — `weight` on each type in `activity_types.json` (clamped 0.1–3.0 in Python).
- **Client preview** — `updateScoreEst()` in `break_reminder_ui.html` (uses selected type’s weight).

---

## How to change break timing

Tunable constants live together near the top of **`break_reminder.py`** (after paths):

- **`INTERVAL_PRESETS`** — Allowed interval lengths (minutes).
- **`WARNING_ADVANCE`** — Seconds before break when the warning panel appears.
- **`IDLE_THRESHOLD`** — Idle seconds before the user stops accumulating “active” time.

Some of these are also surfaced on **`GET /api/config`** for future UI.

---

## Known quirks

- **`lang`** is stored in multiple places: `_g["lang"]`, `config.json`, and sometimes **`localStorage`** (`br_lang`) in the break overlay — keep behavior consistent when changing language.
- **History edit** paths may adjust `total_score` incrementally rather than recomputing from scratch — don’t assume full recalculation after edits.

---

## Client JS sharing

**`shared.js`** provides `window.RS` (`loadActivityTypes`, `ACT_COLORS`, `ACT_LABEL`, `fmtMin`, `saveActivityTypes`, `renderTypeManager`) plus legacy `window.loadActivityTypes`, etc. Load it before inline scripts: `<script src="/shared.js"></script>`.

After `loadActivityTypes()`, one-argument **`ACT_COLORS(id)`** uses an internal cache of the last loaded types.
