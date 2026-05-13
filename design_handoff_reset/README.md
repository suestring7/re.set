# Handoff: re.set — UI Refinement

## Overview

**re.set** is a focus-and-break tracking app. The user works in focused intervals; when an interval ends, a small toast warns them, then a break flow guides them through one quick exercise (stretch, core, or strength), and finally a check-in records what they were focusing on. A records page shows their day from four angles, and a preferences page covers theming, intervals, and language.

This handoff bundles **HTML design references** for refining the visual + interaction design of seven surfaces:

1. Warning toast (pre-break)
2. Break — exercise selection
3. Break — circuit timer
4. Break — check-in
5. Away / Return forms
6. Records (timeline / 24h / weekly bars / heatmap)
7. Preferences

The user-facing copy is **Chinese (zh-CN)**, with an English secondary layer in some places.

---

## About the Design Files

The files in this bundle are **design references created in HTML** — prototypes showing intended look and behavior, **not production code to copy directly**.

The task is to recreate these designs in the target codebase using its established patterns (the existing project has plain `<html>` files served via a small static server with `shared.js`). Take the visual language, layout, type scale, and interactions from these mocks and apply them to the existing app's structure.

The HTML uses inline React + Babel to make iteration fast in the design tool. The target app does **not** use React — port the markup and styles into the existing vanilla-JS template structure (one `.html` per surface, shared CSS via `theme.css`).

## Fidelity

**High-fidelity.** Colors, typography, spacing, border radii, motion, and copy are intended to be implemented as-is. Where exact values are not stated below, lift them from the source (`design/theme.css` and the inline JSX style objects in `design/*.jsx`).

---

## Design System

### Color tokens

All colors come from CSS custom properties in `design/theme.css`. The default theme is **薰衣草 (Lavender)**; four others can be selected in Preferences.

```css
/* Default (Lavender) */
--bg:        #F4EFFA;   /* page background */
--card:      #FFFFFF;   /* surfaces */
--line:      #E8E0F0;   /* dividers, borders */
--text:      #2A1B3D;   /* primary text */
--sub:       #4A3A5C;   /* secondary text */
--muted:     #8B7A9E;   /* tertiary text, captions */
--acc:       #A87FEC;   /* primary accent */
--acc2:      #6B4FA0;   /* darker accent (active states) */
--acc-soft:  #F0E6FB;   /* tinted bg for accent regions */
--green:     #059669;
--amber:     #D97706;
--red:       #DC2626;
```

Alternate themes (apply via `data-theme="<id>"` on `<body>` or a wrapper):

| id        | name (zh / en)    | --acc     | --bg      | --text    |
|-----------|-------------------|-----------|-----------|-----------|
| (default) | 薰衣草 Lavender    | `#A87FEC` | `#F4EFFA` | `#2A1B3D` |
| `sage`    | 鼠尾草 Sage        | `#7BA888` | `#F2F5F2` | `#1F2D24` |
| `mist`    | 雾蓝 Mist          | `#7B9CC4` | `#EFF3F8` | `#1B2A3D` |
| `ochre`   | 赭石 Ochre         | `#C8856B` | `#F8F2EC` | `#2D1F14` |
| `ink`     | 夜墨 Ink (dark)    | `#B794F4` | `#1A1A1F` | `#F0EBF7` |

The full list is in `design/theme.css`. Persist the user's choice (e.g. localStorage key `reset.theme`) and apply on page load before paint to avoid flash.

### Activity-type colors

Used in pills, the 24h proportional bar, and timeline dots. Defined in `uploads/ui/activity_types.json` of the original project; the design uses these values:

| id         | label (zh) | hex       |
|------------|------------|-----------|
| `work`     | 专注 / 工作 | `#A87FEC` (= --acc) |
| `reset`    | Reset      | `#C8B4F0` |
| `meal`     | 用餐       | `#F4C77A` |
| `rest`     | 休息       | `#9DC4E8` |
| `exercise` | 运动       | `#7DC9A0` |
| `social`   | 社交       | `#E89BB5` |
| `other`    | 其他       | `#B8B8B8` |

### Typography

```css
font-family: 'Inter', -apple-system, 'PingFang SC', 'Hiragino Sans GB', sans-serif;
--mono: 'JetBrains Mono', 'SF Mono', ui-monospace, monospace;
```

Type scale used across screens:

| Use                        | size  | weight | family |
|----------------------------|-------|--------|--------|
| Hero numerals (timer)      | 88px  | 200    | mono   |
| Time display (top-bar)     | 32px  | 700    | sans   |
| H2 / page numerals         | 24px  | 700    | sans   |
| Section / item title       | 18px  | 600    | sans   |
| Body                       | 13–14px | 400  | sans   |
| Captions                   | 11–12px | 500–600 | sans |
| Eyebrow / label (uppercase) | 10.5–11px | 700, letter-spacing 1.4–1.6px | sans |
| Numerical data             | (any) | 300–600 | mono, `font-variant-numeric: tabular-nums` |

Always pair Chinese with the same weight as Latin; do not bold Chinese unless explicit.

### Spacing & radii

- Page padding: **24–28px**
- Card padding: **18–24px**
- Card radius: **10–14px** (12 default)
- Pill/chip radius: **99px**
- Input radius: **8–10px**
- Section gap: **14–18px**
- Button height: **40–48px** (`padding: 13–14px`)
- Hairline divider: `1px solid var(--line)`

### Iconography

Custom flat-line SVG glyphs at 32×32 viewBox, `stroke-width: 1.6`, `stroke-linecap: round`. Defined in `design/data-and-icons.jsx` for: neck stretch, shoulder, spine, breath, plank, side plank, bottle press, bottle curl, eye exercise. Each is rendered in the exercise's category color (`--green` stretch / `--amber` core / `--red` strength).

For exercises not yet illustrated, fall back to `DefaultIcon` (a circle).

---

## Screens

### 1. Warning toast (`warning.html`)

**Purpose:** Appears in the corner when a focus interval ends. Counts down ~60 seconds; if the user does nothing, the break starts automatically.

**Recommended variation: A — card style** (other two are exploration).

- **Width** 380px, auto height.
- **Surface** `var(--card)`, **border** 1.5px solid `var(--acc)`, **radius** 14px, **shadow** `0 18px 50px rgba(168,127,236,.25)`.
- **Top row** (padding 18 20 14): 38×38 rounded square in `var(--acc-soft)` holding a coffee/break emoji (or icon), then two-line text block:
  - title: `该休息了` — 14px / 600 / `var(--text)`
  - subtitle: `已专注 42 分钟，眼睛该歇歇了` — 12px / `var(--muted)`
  - right side: countdown `MM:SS` — mono 22px / 300 / `var(--acc2)`, tabular-nums.
- **Progress strip** under the row: 3px tall, full-width, `var(--line)` track with `var(--acc)` fill that decreases linearly with the countdown (`width: ${pct}%; transition: width 1s linear`).
- **Footer** split: left button `再等 5 分钟` (12px / `var(--muted)`); right button `立即开始 →` (12px / 600 / `var(--acc2)`). Divider between is `1px solid var(--line)`.

**Behavior:**
- Countdown ticks every 1s; auto-advance to break flow at 0.
- "+5 分" snoozes 5 minutes (resets countdown to 300s).
- "立即开始" navigates immediately to the selection screen.

### 2. Break — exercise selection

**Purpose:** Pick one of ~9 quick exercises (or skip). Visible: top-bar (clock, daily score, language toggle), goal-progress strip (dots showing today's stretch/core/strength quotas), and the selection grid.

**Recommended variation: A — 3-column icon grid.**

- 3 columns × N rows of cards. Each card 140-ish wide × 110 tall. **Card:** 1.5px border `var(--line)`, radius 10px, padding `14px 12px`, `display:flex; flex-direction:column; gap:6px`.
- Card top row: monospace exercise ID (e.g. `S2`) at 9.5px / 700 / `var(--muted)` left, 32×32 colored SVG icon right.
- Card body: name (13.5px / 600), then mono `2×15s` (11px / `var(--muted)`).
- Card bottom row: a category pill + mono `+8` score.
- **Selected** state: border `var(--acc)`, background `var(--acc-soft)`, transition 150ms.

Below the grid: two text-link footer buttons separated by a hairline middot — `跳过动作` (`var(--muted)`) and `暂停 / 去洗手间` (`var(--acc2)`). 12px, underline-offset 2px.

**Goal-progress strip** above the card:
- Three category groups separated by `·`. Each: a colored pill (`拉伸` green / `核心` amber / `力量` red) + 3-dot progress + `2/3` count in mono 10px.

**Behavior:**
- Tapping a card selects it (single-select). A "Start" button isn't shown in mock A — selection auto-advances after a short confirm in the prototype, but in production you may add an explicit `开始 ▶` button or auto-advance on second tap.

### 3. Break — circuit timer

**Recommended: ring style** (`CircuitB`). Other variations available as alternates: numeral-only (A), breath bubble (C, used specifically for breathing exercises like C1).

- Top-bar + goal strip identical to selection.
- Card padding 24px.
- Card header row: `← 返回` link (12px / `var(--muted)`) left; mono caption right `S4 · 第 1 组 / 共 1 组`.
- **Ring:** 260×260 SVG; track `circle r=110, stroke=var(--line), stroke-width=3`; progress `circle r=110, stroke=var(--acc), stroke-width=6, stroke-linecap=round, stroke-dasharray=2π·110, stroke-dashoffset` interpolated from `secs/total`. Rotate `-90deg`. `transition: stroke-dashoffset 1s linear` so it animates per tick.
- **Center stack** absolute-positioned: 42px exercise icon (in category color), then mono `MM:SS` 54px / 300 with tabular-nums, then exercise name 13px / 600.
- Below ring: instruction text 13px / `var(--sub)` / line-height 1.6, padded `0 24px`.
- **Primary action:** full-width button `✓ 完成全部动作` — transparent background, 1.5px border `var(--line)`, color `var(--muted)`, radius 10, padding 14.

**Breath variant (CircuitC, recommended specifically for breathing exercises C1):**
- Two concentric circles (240px outer, 180px inner) that scale in/out every 4s using `transform: scale(0.65 → 1.0)` and `transition: transform 4s cubic-bezier(0.4,0,0.6,1)`. Phase label `吸 气` / `呼 气` switches with the scale.
- Center shows mono countdown the same way.

**Behavior:**
- Setup: when user picks a multi-set exercise (e.g. T1: 3 sets × 30s), the timer counts down each set, then prompts user to confirm completion of that set, then advances. Sets are visualized as 3 progress dots in `CircuitA`; the ring just runs once per set and resets.
- Auto-advance to check-in on completion.

### 4. Break — check-in

**Recommended: A — labeled form.**

Card padding 22 24. Sections separated by `1px solid var(--line)` and 14px gaps:

1. **Eye-rest row** (8px vertical padding):
   - 18px eye glyph + label `眺望 6m 外` (13px / `var(--sub)`).
   - During the 20s rest: mono `00:NN` countdown + skip link `跳过 →`.
   - After: green "✓ 完成" pill — 11px / 600, padding `3px 10px`, `background: rgba(5,150,105,.1)`, color `var(--green)`, radius 99.
2. **Activity type chips:** label `活动类型`, then a wrap of pills. Pill: 12px / 600, padding `5px 12px`, radius 99. Inactive: 1.5px border `var(--line)` / `var(--bg)` background / `var(--muted)` text. Active: no border / activity-color background / `#1a1a1a` text.
3. **Work content input:** label `这段时间在做什么`, `<input>` with `--bg` background, 1.5px `var(--line)` border, radius 10, padding `11px 14px`, 14px font.
4. **Focus duration + score preview row:**
   - Left: `专注时长` label, 72×40 number input (centered, mono) + `分钟` suffix.
   - Right (auto-margin-left): score preview card. `var(--acc-soft)` bg, 1px `var(--acc)` border, radius 10, padding `10px 16px`. Caption `预计获得` 10.5px above mono `+13` 20px / 600 / `var(--acc2)`.
5. **Submit:** full-width primary button `完成打卡 ✓` — `var(--acc)` bg, white text, radius 10, padding 14, 14px / 600.

**Behavior:**
- Eye timer auto-completes at 0; user can skip.
- Activity type defaults to `work`.
- Score updates live based on `focus_minutes × type_weight` (see original `shared.js` `RS.score`).

### 5. Away / Return forms

**Away form** (`away_form.html`) — 520×420 panel, opens when user clicks "I'm leaving". 18px title `要离开了吗？`, 12px subtitle `记录一下这段时间在做什么`. Type chip group (5 types: meal/rest/exercise/social/other). Free-text note input with placeholder `午饭 · 公司食堂`. Footer two-button row: `取消` (1:2 weight, ghost) and `离开 →` (primary).

**Return form** (`return_form.html`) — 520×500. 18px title `欢迎回来 👋`, 12px subtitle stating the away duration (`你刚才离开了 1 小时 23 分`). A summary card showing the inferred away record (chip + time range + note + an `编辑这段记录` link). Two stat cards: `今日专注 3h 12m` (left) and `积分 ★ 42` (right, accent-tinted). Primary action `开始新一段专注 ▶`.

### 6. Records

The records page has **four equally-weighted views** with a segmented switcher in the top-right:

```
[ 时间线 ]  [ 24h ]  [ 趋势 ]  [ 热图 ]
```

Switcher style: row of 4 mono 11px / 600 buttons, each in its own segment of a `1px var(--line)` outer border (rounded 6px). Active segment: `var(--text)` bg / `var(--bg)` color. Inactive: transparent / `var(--muted)`.

**Common stats strip** at top of every records card:

```
专注 4h 12m   |   Reset 4 次   |   积分 ★ 92   |   连续 7 天
```

Four columns, each: 10.5px caption + 20px mono 300 number with tabular-nums. Bottom border 1px `var(--line)` separating from the view body.

#### 6a. 时间线 / Timeline

Vertical event list with a hairline rail. Each row: timestamp (mono 10.5px, right-aligned, 50px wide), 9px circle marker on the rail (filled with the type color, or hollow with `--acc` border for `reset` events), then label + duration + optional `+score`. Reset events have an extra `RESET` micro-tag (11px / 700 / `var(--acc2)`) before the label.

Rail position: `absolute left:54px`, top/bottom 6px, 1px wide, `var(--line)`.

#### 6b. 24h / Proportional bar

A single 54-tall horizontal bar showing the day from 9:00 → 18:00. Each segment is absolutely positioned by start/end percentages, colored by activity type. `reset` segments are inset top/bottom by 6px and rounded (3px) to read as little capsules sitting inside the work blocks. Hour ticks below in mono 10px.

Below the bar, an **"占比" stacked bar** (1 segment per type, total 100%, height 20px, radius 6px), and a legend row (9×9 colored squares + label).

#### 6c. 趋势 / Weekly bars

Headline pair: `本周专注 23.8h` (mono 32px / 300) and `本周积分 ★ 391`. Trend delta tag right: `↑ 18% 比上周` (11px / 600 / `var(--green)`).

7 vertical bars, one per day. Active day uses `var(--acc)`; future days use `var(--line)` at .5 opacity (ghosted); past days use `var(--text)`. Above each bar, the daily focus hours (mono 10px). Inside each bar, the daily score `★92` (10px mono, `#fff`). Bottom labels (`周一`–`周日`); today bolded in `var(--acc2)`.

#### 6d. 热图 / Heatmap + Achievements

12-column × 7-row grid (12 weeks × 7 days). Cell is 14×14, gap 3, radius 3. Five intensity levels mapped to opacities of `var(--acc)`: 0 (empty cell with `var(--line)` border) → 4 (solid `--acc`). Day-of-week labels left of grid (mono 9.5px, `一二三四五六日`). Top labels: `12周前 / 9周前 / 6周前 / 3周前 / 本周`. Legend row right-aligned: `少 [□□■■■] 多`.

**Achievements section** below (1px top divider): 3 cards in a flex row, each with a 24px emoji + title (12px / 600) + description (10.5px / `--muted`). Examples: `🌱 坚持一周 / 7 天连续打卡`, `👁 眼明手快 / 完成 30 次眺望`, `💪 小有所成 / 累计 100 次 reset`.

### 7. Preferences

Single 660-wide card with 5 sections separated by hairlines:

1. **休息提醒** — Toggle (custom 42×24 pill switch with sliding 20×20 thumb), then two range sliders side-by-side: `专注间隔` (20–90 min, step 5, default 45) and `预警时长` (15–120 sec, step 5, default 60). Slider uses `accent-color: var(--acc)`. Each slider has a header row showing label + current value (mono).
2. **外观** — 4 theme-card grid (薰衣草 / 鼠尾草 / 雾蓝 / 赭石). Each card shows the theme's bg color + 3 swatch dots (acc / dark / white) + name. Selected: 2px solid acc border. Below: a `深色模式` segmented control (浅色 / 深色 / 跟随系统).
3. **语言** — Title + English subtitle, segmented `中文 / English` toggle on the right.
4. **声音** — Two rows: `提醒铃声 [清亮 ▾]` and `完成音效 [柔和 ▾]`. Right side is a faux-select button (8px radius, `--bg` bg).
5. **数据** — Three buttons in a row: `导出 JSON`, `导出 CSV`, `清空数据` (red border + red text).

---

## Interactions & Behavior

| Surface             | Trigger                                           | Action                                    |
|---------------------|---------------------------------------------------|-------------------------------------------|
| Warning toast       | Focus timer hits configured interval              | Slide in from corner, start countdown     |
| Warning toast       | Countdown reaches 0, no input                     | Auto-open break selection                 |
| Warning toast       | "再等 5 分钟"                                      | Reset countdown to 300s                   |
| Selection           | Card tap                                          | Select; show subtle pulse                 |
| Selection           | "跳过动作"                                          | Skip exercise → straight to check-in      |
| Selection           | "暂停 / 去洗手间"                                   | Submit a `restroom` event, return to work |
| Circuit             | Timer hits 0 (single set)                         | Advance to check-in                       |
| Circuit             | Timer hits 0 (multi-set)                          | Pause + show "完成第 N 组" confirmation   |
| Circuit             | "← 返回"                                            | Return to selection (discard timer state) |
| Check-in            | Eye timer hits 0                                  | Auto-mark "✓ 完成"; user may also skip    |
| Check-in            | "完成打卡 ✓"                                       | Persist record, dismiss break flow        |

**Animation:**
- Page transitions: 200ms `cubic-bezier(0.4,0,0.2,1)` opacity + 8px Y slide.
- Pill/button hover: 150ms color/border transitions.
- Ring progress: `transition: stroke-dashoffset 1s linear` (matches the per-second tick).
- Breath bubble: `transition: transform 4s cubic-bezier(0.4,0,0.6,1)`.

**Keyboard:** Spacebar pauses/resumes the circuit timer. Esc returns to selection. Arrow keys navigate between exercises in the grid.

---

## State (per record)

A check-in record (extends the original `shared.js` shape):

```ts
{
  time:           "HH:MM",                  // local
  date:           "YYYY-MM-DD",
  exercise:       Exercise | null,          // null if skipped
  work_content:   string,                   // free text
  focus_minutes:  number,
  activity_type:  "work"|"entertainment"|"life"|"self_improvement"|...,
  eye_done:       boolean,
  score:          number,                   // computed
  event_type?:    "restroom"|"away"|null,
}
```

`score = focus_minutes * activity_weight + (exercise?.score ?? 0) + (eye_done ? 2 : 0)` — preserve the existing `RS.score()` formula in `shared.js`.

Daily score is sum of the day's records.

---

## Files in this bundle

```
prototypes/
├── re.set — Prototype.html        ← wired clickable flow with theme tweaks
├── re.set — Design Canvas.html    ← every variation side-by-side
└── design/
    ├── theme.css                  ← color tokens for all 5 themes (lift directly)
    ├── data-and-icons.jsx         ← exercise SVG icons + sample data
    ├── break-selection.jsx        ← 3 variations of screen 2
    ├── circuit.jsx                ← 3 variations of screen 3
    ├── checkin.jsx                ← 3 variations of screen 4
    ├── warnings-forms.jsx         ← 3 toasts + away/return forms
    ├── records.jsx                ← 4 records views
    ├── preferences.jsx            ← preferences page
    ├── design-canvas.jsx          ← canvas helper (not for production)
    └── tweaks-panel.jsx           ← tweaks helper (not for production)
```

To browse:
1. Open `re.set — Prototype.html` for the wired flow + theme switcher (Tweaks panel, bottom-right).
2. Open `re.set — Design Canvas.html` to see every variation laid out together. Pan/zoom, drag-reorder, double-click for fullscreen.

**Recommended variations** (the others are alternates):
- Warning: A (card)
- Selection: A (icon grid)
- Circuit: B (ring), with C (breath) for breathing exercises only
- Check-in: A (labeled form)
- Records: 4 views with tab switcher in the corner
- Preferences: single page

---

## Notes for the implementer

- **No frameworks needed** — the existing app is plain HTML + a tiny `shared.js`. Port the visuals into that structure. Style via a single `theme.css` (lift `design/theme.css` directly).
- **SVG icons** can be inlined into each HTML file or loaded from a sprite sheet. The 9 exercises shown in `data-and-icons.jsx` cover the main categories; remaining exercises in `exercises.json` should reuse a category-default icon until illustrated.
- **Theme persistence:** read `localStorage.getItem('reset.theme')` on `<head>` boot, set `document.body.dataset.theme` before paint to avoid flash.
- **Tab labels in the records view of the prototype currently render unusual values** (newline characters) — this was an experimental edit. The intended labels are `时间线 / 24h 比例 / 周趋势 / 热图`.
- **Ignore** `design/tweaks-panel.jsx` and `design/design-canvas.jsx` — these are the design tool's chrome, not part of the product.
