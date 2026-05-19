# re.set — UI & Event Logic Reference

## 1. Pages overview

| URL | HTML file | Description |
|-----|-----------|-------------|
| `/` | `break_reminder_ui.html` | Main break window (exercise selection, timer, check-in) |
| `/records` | `records_ui.html` | Daily records viewer (timeline, 24h bar, heatmap, bars) |
| `/preferences` | `preferences.html` | Settings: General / Scoring / Activities / Features / Plan |
| `/away-form` | `away_form.html` | Log work before going away |
| `/return-form` | `return_form.html` | Log return from away period |
| `/plan-today` | `plan_today.html` | 10-min countdown to write today's plan |
| `/warning` | `warning.html` | Small warning panel ("break in X seconds") |

---

## 2. CSS theming system

### Design tokens (`ui/theme.css`)

All colors are CSS custom properties on `:root`. The default (lavender) theme is defined directly in `:root {}`. Other themes override specific vars using attribute selectors:

| Token | Default (lavender) | Role |
|-------|--------------------|------|
| `--bg` | `#F4EFFA` | Page background |
| `--card` | `#FFFFFF` | Card/surface background |
| `--line` | `#E8E0F0` | Borders, dividers |
| `--text` | `#2A1B3D` | Primary text |
| `--sub` | `#4A3A5C` | Secondary text |
| `--muted` | `#8B7A9E` | Muted/disabled text |
| `--acc` | `#A87FEC` | Accent — buttons, active states, slider |
| `--acc2` | `#6B4FA0` | Deep accent — save button, score |
| `--acc-soft` | `#F0E6FB` | Accent tint background |
| `--green` | `#059669` | Positive/success |
| `--amber` | `#D97706` | Warning |
| `--red` | `#DC2626` | Danger/error |
| `--mono` | `'SF Mono', monospace` | Monospace font |

### Preset themes

Activated by `data-theme="<id>"` on `<html>`:

| ID | Chinese | Accent | Background |
|----|---------|--------|-----------|
| *(none)* | 薰衣草 (default) | `#A87FEC` | `#F4EFFA` |
| `sage` | 鼠尾草 | `#7BA888` | `#F2F5F2` |
| `mist` | 雾蓝 | `#7B9CC4` | `#EFF3F8` |
| `ochre` | 赭石 | `#C8856B` | `#F8F2EC` |
| `ink` | 暗黑 | `#B794F4` | `#1A1A1F` |

### Appearance override

Activated by `data-appearance="dark|light"` on `<html>`. `dark` overrides any selected preset with ink colors. `light` is explicit light (mainly used to block system dark mode). No attribute = system/auto.

CSS cascade priority (lowest to highest):
1. Boot-injected fallback `:root` (lavender vars — prevents white-on-white if theme.css fails)
2. `theme.css` `[data-theme]` rules (preset themes)
3. `theme.css` `[data-appearance="dark"]` rule (overrides preset)
4. Inline `style.setProperty('--*')` on `<html>` (custom colors, applied live)

### Custom colors

Stored in `localStorage.reset_custom_colors` as JSON `{acc, acc2, bg, card, text, line}`. Applied as inline style properties on `<html>`, which gives them the highest CSS specificity and overrides any preset.

### Boot snippet (all HTML files)

Every page has this as the very first `<script>` in `<head>`:

```js
(function(){
  // 1. Inject lavender fallback vars (prevents white flash if theme.css 404s)
  var s = document.createElement('style');
  s.textContent = ':root{--bg:#F4EFFA;--card:#fff;...}';
  document.head.insertBefore(s, document.head.firstChild);
  // 2. Restore selected preset theme
  var t = localStorage.getItem('reset_theme');
  if (t) document.documentElement.setAttribute('data-theme', t);
  // 3. Restore appearance mode
  var a = localStorage.getItem('reset_appearance');
  if (a === 'dark') document.documentElement.setAttribute('data-appearance', 'dark');
  else if (a === 'light') document.documentElement.setAttribute('data-appearance', 'light');
  // 4. Restore custom color overrides
  var c = localStorage.getItem('reset_custom_colors');
  if (c) try { var o = JSON.parse(c), r = document.documentElement;
    Object.keys(o).forEach(function(k){ r.style.setProperty('--' + k, o[k]); });
  } catch(e) {}
})()
```

### localStorage keys summary

| Key | Values | Set by |
|-----|--------|--------|
| `reset_theme` | `sage` / `mist` / `ochre` / `ink` / *(absent = lavender)* | `selectTheme()` in preferences.html |
| `reset_appearance` | `light` / `dark` / `system` | `setAppearance()` in preferences.html |
| `reset_custom_colors` | JSON `{acc, acc2, bg, card, text, line}` | `saveCustomColors()` in preferences.html |

---

## 3. HTTP server routes

### GET routes

| Path | Handler | Returns |
|------|---------|---------|
| `/` | `break_reminder_ui.html` | Break window HTML |
| `/records` | `records_ui.html` | Records viewer HTML |
| `/preferences` | `preferences.html` | Preferences HTML |
| `/away-form` | `away_form.html` | Away form HTML |
| `/return-form` | `return_form.html` | Return form HTML |
| `/warning` | `warning.html` | Warning panel HTML |
| `/plan-today` | `plan_today.html` | Plan today HTML |
| `/shared.js` | `shared.js` | Shared JS helpers |
| `/theme.css` | `theme.css` | Design tokens CSS |
| `/api/status` | `_api_status` | Timer state dict |
| `/api/records` | `_api_records` | Today's records JSON |
| `/api/config` | `_api_config` | App config constants |
| `/api/exercises` | `_api_exercises` | Exercise suggestions |
| `/api/history/list` | `_api_history_list` | History date index |
| `/api/history/date?d=YYYY-MM-DD` | `_api_history_date` | Records for specific date |
| `/api/activity-types` | `_api_activity_types_get` | Activity type list |
| `/api/prefs` | `_api_prefs_get` | All prefs JSON |
| `/api/export` | `_api_export` | Download JSON or CSV (`?format=csv`) |

### POST routes

| Path | Handler | Body | Effect |
|------|---------|------|--------|
| `/api/checkin` | `_api_checkin` | `{focus_minutes, work_content, exercise, activity_type}` | Saves break check-in |
| `/api/away-checkin` | `_api_away_checkin` | `{focus_minutes, work_content, activity_type}` | Logs away session |
| `/api/return-log` | `_api_return_log` | `{activity_type, work_content, before}` | Logs return from away |
| `/api/close` | `_api_close` | `{emergency}` | Closes break window |
| `/api/close-popup` | `_api_close_popup` | — | Closes aux window |
| `/api/snooze` | `_api_snooze` | — | Snoozes break by 5 min |
| `/api/postpone-warning` | `_api_postpone_warning` | — | Postpones warning panel |
| `/api/trigger` | `_api_trigger` | — | Triggers break immediately |
| `/api/pause` | `_api_pause` | — | Pauses timer, opens away flow |
| `/api/away` | `_api_away` | — | Logs restroom/away quickly |
| `/api/restroom` | `_api_restroom` | — | Alias for `/api/away` |
| `/api/end-of-day` | `_api_end_of_day` | — | Toggles end-of-day state |
| `/api/prefs` | `_api_prefs_post` | `{interval_minutes, warning_advance_seconds, reminder_enabled, lang, activity_types, menu_features, plan_*}` | Saves all prefs |
| `/api/activity-types` | `_api_activity_types_post` | `[{id, label, color, weight, parent_id}]` | Saves activity types |
| `/api/records/edit` | `_api_records_edit` | `{date, index, ...fields}` | Edits a check-in |
| `/api/records/delete` | `_api_records_delete` | `{date, index}` | Deletes a check-in |
| `/api/plan/save` | `_api_plan_save` | `{text}` | Saves plan to target file |
| `/api/reset-data` | `_api_reset_data` | — | Clears today's session data |

---

## 4. preferences.html — button/event map

### General tab

| Element | Event | Function | Effect |
|---------|-------|----------|--------|
| Reminder pill (`#pill-reminder`) | `onclick` | `toggleReminderPill()` | Toggles `reminderEnabled` bool; updates pill class |
| Focus interval slider (`#rng-interval`) | `oninput` | `onIntervalInput()` | Updates `curInterval`; refreshes display label |
| Warning slider (`#rng-warning`) | `oninput` | `onWarningInput()` | Updates `curWarningSec`; refreshes display label |
| Theme cards (`.theme-card`) | `onclick` | `selectTheme(id)` | Sets `data-theme`, saves to `localStorage.reset_theme`, clears custom overrides |
| Custom tile | `onclick` | `selectTheme('custom')` | Toggles `#custom-panel` open/closed |
| Custom color pickers (`#cp-*`) | `oninput` | `onCustomColorInput(key, val)` | Immediately sets `--key` as inline style |
| Apply custom btn (`#cp-save-btn`) | `onclick` | `saveCustomColors()` | Reads pickers → saves to `reset_custom_colors`, clears preset theme |
| Clear custom btn (`#cp-clear-btn`) | `onclick` | `clearCustomColors()` | Removes `reset_custom_colors`, removes inline styles |
| Appearance seg (`#app-light/dark/sys`) | `onclick` | `setAppearance(mode)` | Sets/removes `data-appearance`, saves to `reset_appearance` |
| Lang seg (`#lang-zh/en`) | `onclick` | `selLang = 'zh'/'en'; renderLangSeg()` | Marks selection (saved on Save) |
| Export JSON (`#btn-exp-json`) | `onclick` | `exportData('json')` | GET `/api/export` → download |
| Export CSV (`#btn-exp-csv`) | `onclick` | `exportData('csv')` | GET `/api/export?format=csv` → download |
| Clear data (`#btn-reset-data`) | `onclick` | `resetData()` | Confirm → POST `/api/reset-data` |

### Other tabs

| Tab | Key elements | On render |
|-----|-------------|-----------|
| Scoring | Weight inputs per activity type | `renderWeights()` (called when tab selected or types saved) |
| Activities | Color + label + parent for each type; add/delete | `renderPrefTypeManager()` (full re-render on mutation) |
| Features | Toggle checkboxes per menu item | `renderFeatureToggles()` (called when tab selected) |
| Plan | File path, keyword, not-found action, prefix type | Loaded from `/api/prefs`, saved with main Save button |

### Save button (`#btn-save`)

Calls `saveAll()` → POST `/api/prefs` with:
- `interval_minutes`, `warning_advance_seconds`, `reminder_enabled`
- `lang`, `activity_types`, `menu_features`
- `plan_file_path`, `plan_file_keyword`, `plan_prefix_type`, `plan_prefix_custom`, `plan_keyword_not_found`

Theme / appearance / custom colors are **localStorage-only** and take effect immediately without Save.

---

## 5. records_ui.html — view modes

| Button | View activated | Render function |
|--------|---------------|-----------------|
| `#vtab-events` | Event timeline | `renderTimeline()` |
| `#vtab-24h` | 24-hour proportional bar | `render24h()` |
| `#vtab-heatmap` | 12-week GitHub-style heatmap | `renderHeatmap()` |
| `#vtab-bars` | Stacked/timeline bar charts | `renderBars()` |

Date navigation: `◀` / `▶` arrows call `loadDate(offset)`. "Today" button reloads today.

---

## 6. Deployment requirement

**Source file changes do NOT appear in the running app automatically.** The `.app` bundle contains compiled `.pyc` files. After every code change:

```bash
# From project root:
bash packaging/build_app.sh

# Then in Terminal (NOT from Cursor):
pkill "re.set"
rm -rf ~/Applications/re.set.app
cp -R dist/re.set.app ~/Applications/
open ~/Applications/re.set.app
```
