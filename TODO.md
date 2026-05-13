# re.set — Master TODO

_Last updated: 2026-05-12_

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

- **UI Redesign — Design Handoff** (6 steps, see plan below)

### 🟡 APPROVED — Queued

_(awaiting implementation)_

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
- [ ] `0a` Create `ui/theme.css` (lifted from `design/theme.css`, 5 themes)
- [ ] `0b` Add SVG exercise icons to `shared.js` (9 icons by id, fallback DefaultIcon)
- [ ] `0c` Add theme-boot snippet (reads `localStorage` before paint, sets `data-theme`)

### Step 1 — `warning.html`
- [ ] `1a` Variation A card: 380px, 1.5px acc border, ☕ icon in acc-soft, countdown, progress strip
- [ ] `1b` Footer: "再等 5 分钟" / "立即开始 →" with hairline divider

### Step 2 — `break_reminder_ui.html` (4 internal views)
- [ ] `2a` Link `theme.css`; update all CSS tokens to new design system
- [ ] `2b` New topbar: 32px/700 clock, ★ score pill (acc-soft bg + acc border), muted date
- [ ] `2c` Selection (3 cards): SVG icon top-right, acc-soft selected state, new card layout
- [ ] `2d` Circuit — default: SVG ring (260×260, stroke-dashoffset, 1s linear transition)
- [ ] `2e` Circuit — breathing (ex.id === 'C1'): breath bubble variant (scale 0.65↔1.0, 4s ease)
- [ ] `2f` Check-in: acc-soft score box, updated spacing/radius, new label style
- [ ] `2g` Away/return: align tokens to new palette

### Step 3 — `records_ui.html`
- [ ] `3a` 4-segment tab switcher (时间线 / 24h 比例 / 周趋势 / 热图)
- [ ] `3b` Stats strip: 4 columns (专注 / Reset次 / 积分 / 连续天), mono 20px/300
- [ ] `3c` Timeline: left rail at 54px, mono timestamps right-aligned, RESET micro-tag
- [ ] `3d` 24h bar: proportional segments by type color, inset reset capsules, stacked breakdown
- [ ] `3e` Weekly bars: 32px mono headline, bar chart with score inside bars, day labels
- [ ] `3f` Heatmap: GitHub style (12 cols × 7 rows, Mon top, 12×12px, gap 3, 5 levels), achievements section

### Step 4 — `preferences.html` — General tab only
- [ ] `4a` Section 1: reminder toggle (42×24 pill) + two range sliders (interval / warning)
- [ ] `4b` Section 2: 4 theme cards + dark mode segmented (浅色/深色/跟随系统)
- [ ] `4c` Section 3: language segmented control (existing logic, new style)
- [ ] `4d` Section 4: sound rows (UI only, no audio backend)
- [ ] `4e` Section 5: data buttons (导出 JSON / 导出 CSV / 清空数据)

### Step 5 — Backend additions for new prefs
- [ ] `5a` Add `warning_advance_seconds` as user-configurable (AppConfig + persistence + `/api/prefs`)
- [ ] `5b` Add `reminder_enabled` flag (AppConfig + persistence + `/api/prefs`)

### Step 6 — Theme wiring across all pages
- [ ] `6a` `<link>` to `theme.css` + theme-boot snippet in every HTML head
- [ ] `6b` Theme selection in Preferences writes `localStorage` + updates `data-theme` live

---

## Review Log

**2026-05-12 — UI Redesign proposal**
- [Architect] Approved. theme.css approach keeps tokens centralized; SVG ring is pure CSS/JS; no new API endpoints for steps 0–3; steps 5a/5b are small and bounded.
- [Designer] Approved with notes: 3-card layout is better for focus (less overwhelming). GitHub heatmap is cleaner than custom grid. Sidebar-nav preservation keeps familiarity.
- [Coach] Approved. 3-card pick still covers all three categories per rotation. Breath bubble for C1 is the right special case.
- [Auditor] Green light. Scope is well-bounded. User adjustments (3 cards, GitHub heatmap, General tab only) all improve the plan.
