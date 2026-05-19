# re.set — Master TODO

_Last updated: 2026-05-15_

---

## Agent Roster

| Agent | Role |
|-------|------|
| **[Architect]** | Technical soundness — PyObjC stability, threading, core/platform boundary |
| **[Designer]** | UI/UX quality — layout, visual polish, interaction feel |
| **[Coach]** | Training science — exercise selection, rest logic, movement programming |
| **[Auditor]** | Final review — does the feature actually serve the user? Green-light or send back |

---

## TODO List

### 🟢 DONE

- Bug fix: date rollover — `today_record` now refreshes on midnight tick
- Bug fix: break window frame — repositions to current main screen on each show
- Bug fix: cmd+esc emergency exit — NSEvent monitor registered at launch

### 🔵 IN PROGRESS

- **示意图 infrastructure** — images to be generated (DALL-E 3 recommended); serving route in http_server.py (`/exercises/img/`) already wired; display in break circuit view still pending
- **肌群 SVG 形状** — 用户正在用 Inkscape 从 `user_input/muscle_distribution.png` 手动扣图; Python 坐标校准完成 (figure center x_crop=330, scale 0.253/0.247); 等待用户提供 path d= 数据后替换 `records_ui.html` frontSVG/backSVG

### 🟡 APPROVED — Queued

_(all items implemented — see DONE below)_

### 🟢 DONE (recently completed)

- **Items [1]–[7] batch** ✅
  - [1] Heatmap scroll: `renderHeatmap()` now sets `scrollLeft=scrollWidth` after render
  - [2] Exercise stars: `/api/exercise-stats` endpoint; hover panel shows count + ☆/★/★★/★★★ + progress bar fill
  - [3] Timeline cards: work_content promoted to primary (13px/600); exercise name demoted (11px/muted); score format fixed (`+-11` → `-11`)
  - [4] Exercise form: sets + duration_per_set fields added; saved to user_exercises.json; duration_seconds = sets × duration_per_set
  - [5] Pre-away tracking: already implemented — `return_form.html` has "before you left" section, backend `_api_return_log` handles `before_leave`
  - [6] Restroom analytics: big/small sub-chips in away view; `event_type="restroom"` set when activity="restroom"; `/api/restroom-stats` endpoint; "洗手间" tab in records_ui (gated by `menu_features.restroom_analytics`); feature toggle in Preferences
  - [7] Scheduled alerts: `AppConfig.scheduled_alerts` list; `AppViewModel._check_scheduled_alerts()` on each tick; `show_custom_alert` Observable; controller subscribes and opens `custom_alert.html`; `/api/alerts` GET/POST; alert management UI in Preferences → Features tab

- **Items 2–8 batch** ✅
  - Timer drift fix: `_loop()` uses `_dt` (monotonic delta) instead of hardcoded 1
  - Warning advance default raised to 90s
  - Exercise library: `difficulty`, `illustration`, `muscle_focus`, `pain_contraindications` fields added; scores rebalanced (stretch 3–4, core 2–3, strength 3–4); T10 `requires_props` fixed; 3 new exercises (S12, C11, T11)
  - Minimums-met streak: streak counts only days where all category minimums are met (`minimums_met` field in history list)
  - Heatmap: green cells for minimums-met days, purple for partial, dual legend
  - Body muscle graph: new "肌群" tab in records with SVG front/back diagram, training frequency coloring, `/api/muscle-stats` endpoint
  - Exercise preferences: `exercise_standing`, `exercise_props`, `exercise_max_difficulty`, `pain_flags` in AppConfig; ExerciseService filters pool; new "运动" tab in Preferences with pain-area flags + exercise library editor
  - Work content: no longer required (validation removed from `checkReady()`)
  - User-contributed exercises: `/api/exercises/library` GET/POST, `user_exercises.json` in data dir
  - Image serving: `/exercises/img/` route ready for 示意图 when images are generated

- **Alarm sounds** ✅ — audio feedback for break reminder and check-in completion
  - `AppConfig`: `reminder_sound = "Ping"`, `done_sound = "Tink"`
  - `persistence.py` + `prefs_vm`: full round-trip via `GET /api/prefs` + `POST /api/prefs`
  - `controller.py`: `NSSound.soundNamed_()` plays on `showBreakWindow_` and via `playDoneSound_:` selector dispatched from `_api_checkin`
  - Preferences UI already had dropdown stubs; POST saves to backend
- **Exercise cooldown** ✅ — exercises done in last 30 min are deprioritised in pick_exercises
- **Timer refactor** ✅ — simplified dual `_reminders_enabled` check in `break_timer.py`

### ⚪ PROPOSED — Under Review

_(nothing under review)_

### 🔴 REJECTED

_(nothing rejected yet)_

---

## Active Plan — UI Redesign (Design Handoff)

### Confirmed constraints
- Exercise selection: **3 cards only** (existing `/api/exercises` picks 3; new design applies to those same 3)
- Heatmap: **GitHub style** — weeks as columns, Mon→Sun as rows, 12×12px cells, gap 3px, 5 opacity levels on `--acc`
- Preferences: **sidebar-nav stays**; new 5-section single-card layout is the **General tab only**

### Step 0 — Foundation
- [x] `0a` Create `ui/theme.css` (lifted from `design/theme.css`, 5 themes)
- [x] `0b` Add SVG exercise icons to `shared.js` (9 icons by id, fallback DefaultIcon)
- [x] `0c` Add theme-boot snippet (reads `localStorage` before paint, sets `data-theme`)

### Step 1 — `warning.html`
- [x] `1a` Variation A card: 380px, 1.5px acc border, ☕ icon in acc-soft, countdown, progress strip
- [x] `1b` Footer: "再等 5 分钟" / "立即开始 →" with hairline divider

### Step 2 — `break_reminder_ui.html` (4 internal views)
- [x] `2a` Link `theme.css`; update all CSS tokens to new design system
- [x] `2b` New topbar: 32px/700 clock, ★ score pill (acc-soft bg + acc border), muted date
- [x] `2c` Selection (3 cards): SVG icon top-right, acc-soft selected state, new card layout
- [x] `2d` Circuit — default: SVG ring (260×260, stroke-dashoffset, 1s linear transition)
- [x] `2e` Circuit — breathing (ex.id === 'C1'): breath bubble variant (scale 0.65↔1.0, 4s ease)
- [x] `2f` Check-in: acc-soft score box, updated spacing/radius, new label style
- [x] `2g` Away/return: align tokens to new palette

### Step 3 — `records_ui.html`
- [x] `3a` 4-segment tab switcher (时间线 / 24h 比例 / 周趋势 / 热图)
- [x] `3b` Stats strip: 4 columns (专注 / Reset次 / 积分 / 连续天), mono 20px/300
- [x] `3c` Timeline: left rail at 54px, mono timestamps right-aligned, RESET micro-tag
- [x] `3d` 24h bar: proportional segments by type color, inset reset capsules, stacked breakdown
- [x] `3e` Weekly bars: 32px mono headline, bar chart with score inside bars, day labels
- [x] `3f` Heatmap: GitHub style (12 cols × 7 rows, Mon top, 12×12px, gap 3, 5 levels), achievements section

### Step 4 — `preferences.html` — General tab only
- [x] `4a` Section 1: reminder toggle (42×24 pill) + two range sliders (interval / warning)
- [x] `4b` Section 2: 4 theme cards + dark mode segmented (浅色/深色/跟随系统)
- [x] `4c` Section 3: language segmented control (existing logic, new style)
- [x] `4d` Section 4: sound rows (UI only, no audio backend)
- [x] `4e` Section 5: data buttons (导出 JSON / 导出 CSV / 清空数据)

### Step 5 — Backend additions for new prefs
- [x] `5a` Add `warning_advance_seconds` as user-configurable (AppConfig + persistence + `/api/prefs`)
- [x] `5b` Add `reminder_enabled` flag (AppConfig + persistence + `/api/prefs`)

### Step 6 — Theme wiring across all pages
- [x] `6a` `<link>` to `theme.css` + theme-boot snippet in every HTML head
- [x] `6b` Theme selection in Preferences writes `localStorage` + updates `data-theme` live

---

## Review Log

**2026-05-12 — UI Redesign proposal**
- [Architect] Approved. theme.css approach keeps tokens centralized; SVG ring is pure CSS/JS; no new API endpoints for steps 0–3; steps 5a/5b are small and bounded.
- [Designer] Approved with notes: 3-card layout is better for focus (less overwhelming). GitHub heatmap is cleaner than custom grid. Sidebar-nav preservation keeps familiarity.
- [Coach] Approved. 3-card pick still covers all three categories per rotation. Breath bubble for C1 is the right special case.
- [Auditor] Green light. Scope is well-bounded. User adjustments (3 cards, GitHub heatmap, General tab only) all improve the plan.
