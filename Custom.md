# re.set — Customization Guide

Everything here is designed to be changed **without touching core logic**. Each section tells you exactly which file to edit and what to change.

---

## 1. Color Themes

### Built-in presets
All five preset themes live in **`ui/theme.css`**. Each theme is a CSS block like:

```css
[data-theme="sage"] {
  --bg:       #F2F5F2;
  --card:     #fff;
  --line:     #DDE6DD;
  --text:     #1F2D24;
  --sub:      #3A4A40;
  --muted:    #7B8A80;
  --acc:      #7BA888;   /* primary accent — buttons, selected states */
  --acc2:     #4F7359;   /* darker accent — score pill, active text */
  --acc-soft: #E5EFE6;   /* translucent accent — badge backgrounds */
}
```

To **add a new preset**:
1. Add a new block to `ui/theme.css` — e.g. `[data-theme="rose"]{ ... }`
2. Add a new card to `renderThemeCards()` in `ui/preferences.html` (search for `THEMES` constant):
   ```js
   {id:'rose', name:'玫瑰', acc:'#E88080', bg:'#FBF2F2'},
   ```
3. Add the same CSS vars to the inline boot snippet in **all** HTML files (search for `data-theme="ochre"` and add your block after it).

### In-app custom colors
Open **Preferences → General → 外观** and click the **自定义** tile. You can override any of the six key variables live without editing files.

---

## 2. Sound Files

### Built-in NSSound presets
The dropdown in **Preferences → General → 声音** uses macOS built-in sounds:

| Display name | NSSound name | Notes |
|---|---|---|
| 清亮 | `Ping` | Short, bright |
| 叮声 | `Tink` | Delicate click |
| 轻弹 | `Pop` | Short pop |
| 低鸣 | `Purr` | Soft sustained |
| 水滴 | `Submarine` | Sonar-like |
| 莫斯 | `Morse` | Dots |
| 玻璃 | `Glass` | Clear ring |
| 低沉 | `Funk` | Deep bass |
| 英雄 | `Hero` | Heroic chord |
| 吹声 | `Blow` | Wind tone |
| 无声 | `""` | Silence |

### Adding custom sound files (future feature — see TODO.md)
Once the audio backend is wired, place `.aiff` or `.wav` files in:
```
~/Library/Application Support/re.set/sounds/
```
They will appear automatically in the dropdowns at the bottom of the list.

---

## 3. Achievement / Milestone Definitions

Achievements are defined in a single declarative array near the top of `ui/records_ui.html`. Search for `ACHIEVEMENT_DEFS`:

```js
const ACHIEVEMENT_DEFS = [
  {
    icon: '🌱',
    zh: '连续打卡',
    en: 'Daily streak',
    condition: s => s.streak > 0 ? `${s.streak}天连续` : null,
  },
  // ... add yours here
];
```

Each entry receives a `stats` object with these fields:

| Field | Type | Description |
|---|---|---|
| `streak` | `number` | Current consecutive-day streak |
| `totalResets` | `number` | All-time check-in count |
| `totalFocusMin` | `number` | All-time focus minutes |
| `totalDays` | `number` | Days with at least one record |
| `maxDailyScore` | `number` | Highest single-day score |

Return a **subtitle string** when the achievement is earned, `null` when not.

**Example** — add a "Night owl" achievement:
```js
{
  icon: '🦉',
  zh: '夜猫子',
  en: 'Night owl',
  condition: s => s.totalFocusMin >= 100 && s.streak >= 3
    ? (lang==='zh' ? '连续3天深夜打卡' : '3-night streak') : null,
},
```

---

## 4. Activity Types & Colors

Activity types (Work / Entertainment / Life / etc.) and their colors are managed in:
- **`/api/activity-types`** — GET/POST from `ui/preferences.html` → Activities tab
- **`core/models/app_config.py`** — default types defined in `DEFAULT_ACTIVITY_TYPES`

To change a color permanently, edit `DEFAULT_ACTIVITY_TYPES` in `core/models/app_config.py` and delete `~/Library/Application Support/re.set/state.json` to reset to defaults.

---

## 5. Rebuild After Source Changes

After editing any source file, rebuild the app:

```bash
cd /path/to/re.set
bash packaging/build_app.sh
pkill "re.set"
open dist/re.set.app
```
