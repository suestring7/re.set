#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Break Reminder Backend — v3.0
• Smart timer: only accumulates when user is active (Quartz idle detection)
• NSStatusBar: 🌿 menu with timer display + Away button
• PyObjC native window at NSScreenSaverWindowLevel

卸载:
  launchctl unload ~/Library/LaunchAgents/com.user.breakreminder.plist
  rm ~/Library/LaunchAgents/com.user.breakreminder.plist
  rm ~/Desktop/Playground/re.set/break_reminder.py
  rm ~/Desktop/Playground/re.set/break_reminder_ui.html
  rm ~/Desktop/Playground/re.set/exercises.json
"""

# ── Standard library ──────────────────────────────────────────────────────────
import http.server, json, os, random, sys, threading, time
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# ── PyObjC ────────────────────────────────────────────────────────────────────
import objc
from Foundation import NSObject, NSURLRequest, NSURL, NSMakeRect, NSTimer, NSBundle
from AppKit import (
    NSApplication, NSApp,
    NSApplicationActivationPolicyAccessory,
    NSWindow, NSWindowStyleMaskBorderless, NSBackingStoreBuffered,
    NSWindowStyleMaskTitled, NSWindowStyleMaskClosable,
    NSWindowStyleMaskMiniaturizable, NSWindowStyleMaskResizable,
    NSScreen, NSColor,
    NSStatusBar, NSVariableStatusItemLength, NSMenu, NSMenuItem,
    NSStatusWindowLevel, NSFloatingWindowLevel,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
    NSWindowCollectionBehaviorIgnoresCycle,
    NSWorkspace,
)
from WebKit import WKWebView, WKWebViewConfiguration
try:
    from AppKit import NSScreenSaverWindowLevel
except ImportError:
    NSScreenSaverWindowLevel = 1000

# NSPopUpMenuWindowLevel (101) stays above all normal windows and fullscreen
# spaces but — unlike NSScreenSaverWindowLevel (1000) — the OS still treats
# it as a regular key window, so keyboard / mouse input works in WKWebView.
BREAK_WINDOW_LEVEL = 101  # NSPopUpMenuWindowLevel


class BreakWindow(NSWindow):
    """Borderless NSWindow that always accepts key/main window status.

    By default, NSWindowStyleMaskBorderless windows return False from
    canBecomeKeyWindow, which prevents WKWebView from receiving keyboard
    input and causes text fields to appear disabled (greyed out).
    """
    def canBecomeKeyWindow(self):  return True
    def canBecomeMainWindow(self): return True

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR     = Path(__file__).parent.resolve()

def _in_app_bundle() -> bool:
    p = str(sys.argv[0] or "")
    return getattr(sys, "frozen", False) or (".app/Contents/MacOS" in p)

def _bundle_resource_dir() -> Path | None:
    try:
        rp = NSBundle.mainBundle().resourcePath()
        if rp:
            return Path(str(rp))
    except Exception:
        return None
    return None

def resource_path(name: str) -> Path:
    """Read-only app resources (HTML/JS/JSON) for dev + packaged app."""
    if _in_app_bundle():
        rd = _bundle_resource_dir()
        if rd is not None:
            return rd / name
    return SCRIPT_DIR / name

def app_support_dir() -> Path:
    """User-writable state (config/history/logs) – never inside the .app bundle."""
    return Path.home() / "Library" / "Application Support" / "re.set"

APP_SUPPORT_DIR = app_support_dir()

EXERCISES_FILE = resource_path("exercises.json")
UI_FILE        = resource_path("break_reminder_ui.html")
RECORDS_UI_FILE = resource_path("records_ui.html")
PREFERENCES_UI_FILE = resource_path("preferences.html")
AWAY_FORM_FILE = resource_path("away_form.html")
RETURN_FORM_FILE = resource_path("return_form.html")
WARNING_FILE   = resource_path("warning.html")
SHARED_JS_FILE = resource_path("shared.js")
DEFAULT_ACTIVITY_TYPES_FILE = resource_path("activity_types.json")

STATE_FILE     = APP_SUPPORT_DIR / "break_reminder_state.json"
LOG_FILE       = APP_SUPPORT_DIR / "work_log.txt"
CONFIG_FILE    = APP_SUPPORT_DIR / "config.json"
HISTORY_DIR    = APP_SUPPORT_DIR / "history"
ACTIVITY_TYPES_FILE = APP_SUPPORT_DIR / "activity_types.json"

# ── Tunable constants (timing, scoring thresholds, server port) ───────────────
# PORT — HTTP server for WKWebView UI and API.
# INTERVAL_SECONDS — break cycle length in seconds (mutable via menu / prefs).
# WARNING_ADVANCE — seconds before break when the floating warning panel appears.
# SNOOZE_DELAY — extra delay after user snoozes a break.
# IDLE_THRESHOLD — Quartz idle time (seconds) before user counts as inactive.
# DAILY_MINIMUMS — per-category exercise counts required for “all goals met”.
# INTERVAL_PRESETS — allowed break-interval lengths (minutes) in menu + prefs.
# EYE_TIMER_SECONDS — eye-relief countdown on check-in screen; exposed via /api/config.
PORT             = 18030
INTERVAL_SECONDS = 30 * 60   # mutable at runtime via status-bar menu
WARNING_ADVANCE  = 60
SNOOZE_DELAY     = 5 * 60
IDLE_THRESHOLD   = 60
DAILY_MINIMUMS   = {"stretch": 3, "core": 3, "strength": 2}
INTERVAL_PRESETS = [15, 20, 25, 30, 45, 60]  # minutes shown in menu
EYE_TIMER_SECONDS = 20

DEFAULT_ACTIVITY_TYPES = [
    {"id": "work",          "label": "Work",          "color": "#6366F1", "weight": 1.0},
    {"id": "entertainment", "label": "Entertainment", "color": "#EC4899", "weight": 1.0},
    {"id": "life",          "label": "Life",          "color": "#10B981", "weight": 1.0},
]

def load_activity_types() -> list:
    raw: list = []
    if ACTIVITY_TYPES_FILE.exists():
        try:
            raw = json.loads(ACTIVITY_TYPES_FILE.read_text(encoding="utf-8"))
        except Exception:
            raw = []
    elif DEFAULT_ACTIVITY_TYPES_FILE.exists():
        try:
            raw = json.loads(DEFAULT_ACTIVITY_TYPES_FILE.read_text(encoding="utf-8"))
        except Exception:
            raw = []
    if not raw:
        raw = list(DEFAULT_ACTIVITY_TYPES)
    out = []
    for tp in raw:
        if not isinstance(tp, dict) or not tp.get("id"):
            continue
        try:
            w = float(tp.get("weight", 1.0))
        except (TypeError, ValueError):
            w = 1.0
        w = max(0.1, min(3.0, w))
        out.append({**tp, "weight": w})
    return out if out else list(DEFAULT_ACTIVITY_TYPES)


def activity_focus_score_points(fm: int, act_type) -> int:
    """Focus portion of session score: floor(fm * weight / 5)."""
    fm = max(0, int(fm))
    weight = 1.0
    if act_type:
        for tp in load_activity_types():
            if tp.get("id") == act_type:
                try:
                    weight = float(tp.get("weight", 1.0))
                except (TypeError, ValueError):
                    weight = 1.0
                weight = max(0.1, min(3.0, weight))
                break
    return max(0, int(fm * weight / 5))

def save_activity_types(types: list) -> None:
    ACTIVITY_TYPES_FILE.write_text(
        json.dumps(types, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_interval_minutes(mins: int) -> None:
    global INTERVAL_SECONDS
    if mins not in INTERVAL_PRESETS:
        return
    INTERVAL_SECONDS = mins * 60
    with _lock:
        _g["active_seconds"] = min(_g["active_seconds"], INTERVAL_SECONDS - WARNING_ADVANCE - 5)
        if INTERVAL_SECONDS - _g["active_seconds"] > WARNING_ADVANCE:
            _g["warning_shown"] = False
    save_config({"interval_minutes": mins})
    _log(f"Interval → {mins} min")


def apply_language(lang: str) -> None:
    if lang not in ("zh", "en"):
        return
    _g["lang"] = lang
    save_config({"lang": lang})
    _log(f"Language → {lang}")

# ── Status-bar menu i18n ──────────────────────────────────────────────────────
_MI = {
    "zh": {
        "app_title":    "re.set  休息提醒",
        "timer_fmt":    lambda m, s: f"下次休息：{m:02d}:{s:02d}",
        "snooze_fmt":   lambda m, s: f"已推迟：{m:02d}:{s:02d}",
        "paused_fmt":   lambda m, s: f"已暂停  {m:02d}:{s:02d}",
        "pause":        "暂停计时",
        "resume_log":   "回来了，记录一下",
        "away_form":    "记录工作时段",
        "trigger":      "立即触发休息",
        "records":      "查看今日记录",
        "prefs":        "设置",
        "interval":     "休息间隔",
        "lang":         "语言 / Language",
        "lang_zh":      "中文",
        "lang_en":      "English",
        "eod_on":       "下班了",
        "eod_off":      "恢复提醒",
        "quit":         "退出",
        "min_sfx":      " 分钟",
    },
    "en": {
        "app_title":    "re.set  Break Reminder",
        "timer_fmt":    lambda m, s: f"Next break: {m:02d}:{s:02d}",
        "snooze_fmt":   lambda m, s: f"Snoozed: {m:02d}:{s:02d}",
        "paused_fmt":   lambda m, s: f"Paused  {m:02d}:{s:02d}",
        "pause":        "Pause Timer",
        "resume_log":   "I'm back — log it",
        "away_form":    "Log Work Session",
        "trigger":      "Trigger Break Now",
        "records":      "View Today's Records",
        "prefs":        "Preferences",
        "interval":     "Break Interval",
        "lang":         "Language / 语言",
        "lang_zh":      "中文",
        "lang_en":      "English",
        "eod_on":       "End of Day",
        "eod_off":      "Resume Breaks",
        "quit":         "Quit",
        "min_sfx":      " min",
    },
}


def _L(key):
    """Look up a menu-string in the current language."""
    return _MI.get(_g.get("lang", "zh"), _MI["zh"]).get(key, key)


# ── Config persistence ────────────────────────────────────────────────────────
def load_config() -> dict:
    try:
        return json.loads(CONFIG_FILE.read_text()) if CONFIG_FILE.exists() else {}
    except Exception:
        return {}

def save_config(data: dict) -> None:
    try:
        cfg = load_config()
        cfg.update(data)
        CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    except Exception:
        pass

# ── Global state ───────────────────────────────────────────────────────────────
_lock = threading.Lock()
_g: dict = {
    "snooze_available": True,
    "break_locked":    False,
    "active_seconds":  0,
    "warning_shown":   False,
    "snooze_until":    0.0,
    "done_for_today":  False,  # True after "End of Day" — no more breaks until midnight
    "done_for_date":   "",     # the date string when done_for_today was set
    "lang":            "zh",
    "last_checkin_ts": 0.0,
    "skip_exercise":   False,
    "away_mode":       False,  # True while paused (away from desk)
    "away_start_ts":   0.0,   # wall-clock when Pause was clicked
    "postpone_count":  0,     # how many times warning has been postponed this cycle
}
_wc = None   # WindowController (set in main)


# ═════════════════════════════════════════════════════════════════════════════
#  EXERCISE CACHE
# ═════════════════════════════════════════════════════════════════════════════
_exercises_cache: list | None = None

def load_exercises() -> list:
    global _exercises_cache
    if _exercises_cache is None:
        with open(EXERCISES_FILE, encoding="utf-8") as f:
            _exercises_cache = json.load(f)
    return _exercises_cache


# ═════════════════════════════════════════════════════════════════════════════
#  STATE MANAGEMENT
# ═════════════════════════════════════════════════════════════════════════════
def today_str() -> str:
    return date.today().isoformat()

def _default_state() -> dict:
    return {
        "date": today_str(),
        "completed_exercises": [],
        "category_counts": {"stretch": 0, "core": 0, "strength": 0},
        "total_score": 0,
        "focus_minutes": 0,
        "checkins": [],
    }

def _archive_daily_state(state: dict) -> None:
    """Persist a completed day's structured data to history/YYYY-MM-DD.json."""
    d = state.get("date")
    if not d: return
    HISTORY_DIR.mkdir(exist_ok=True)
    p = HISTORY_DIR / f"{d}.json"
    if not p.exists():
        try:
            p.write_text(json.dumps(state, ensure_ascii=False, indent=2))
        except Exception:
            pass

def load_state() -> dict:
    if not STATE_FILE.exists():
        return _default_state()
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            s = json.load(f)
        if s.get("date") != today_str():
            _write_daily_summary(s)
            _archive_daily_state(s)
            return _default_state()
        return s
    except Exception:
        return _default_state()

def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    tmp.replace(STATE_FILE)


# ═════════════════════════════════════════════════════════════════════════════
#  LOGGING
# ═════════════════════════════════════════════════════════════════════════════
def _append_log(text: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text)

def _log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def _write_daily_summary(state: dict) -> None:
    if not state or not state.get("checkins"):
        return
    d, counts = state.get("date",""), state.get("category_counts",{})
    total = state.get("total_score", 0)
    fm    = state.get("focus_minutes", 0)
    ckins = state.get("checkins", [])
    fs    = sum(c.get("focus_minutes",0)//5 for c in ckins)
    exc   = sum(1 for c in ckins if c.get("exercise"))
    h, m  = fm//60, fm%60
    fs_str = f"{h}小时{m}分钟" if h else f"{m}分钟"
    s_ok  = counts.get("stretch",0)  >= DAILY_MINIMUMS["stretch"]
    c_ok  = counts.get("core",0)     >= DAILY_MINIMUMS["core"]
    t_ok  = counts.get("strength",0) >= DAILY_MINIMUMS["strength"]
    names = [c["exercise"]["name"] for c in ckins if c.get("exercise")]
    _append_log(
        f"\n===== {d} 日报 =====\n"
        f"总专注时长：{fs_str}\n"
        f"完成动作：{exc}个（"
        f"拉伸{counts.get('stretch',0)}{'✅' if s_ok else '❌'}/"
        f"核心{counts.get('core',0)}{'✅' if c_ok else '❌'}/"
        f"力量+水瓶{counts.get('strength',0)}{'✅' if t_ok else '❌'}）\n"
        f"保底达标：{'✅ 全部完成' if (s_ok and c_ok and t_ok) else '❌ 未全部完成'}\n"
        f"动作积分：{total-fs}分 | 专注积分：{fs}分 | 总分：{total}分\n"
        f"完成动作列表：{', '.join(names) if names else '无'}\n"
        f"============================\n\n"
    )

def write_log_entry(state: dict, checkin: dict) -> None:
    ns  = datetime.now().strftime("%Y-%m-%d %H:%M")
    fm  = checkin.get("focus_minutes", 0)
    ex  = checkin.get("exercise")
    act = (f"动作：{ex['name']} {ex['id']} (+{ex['score']}分)"
           if ex else "动作：跳过")
    _append_log(
        f"[{ns}] 专注 {fm}min (+{fm//5}分) | {act} | "
        f"本次 +{checkin['score']}分 | 今日累计 {state['total_score']}分 | "
        f"内容：{checkin.get('work_content','')}\n"
    )

def _log_restroom_event() -> None:
    ns = datetime.now().strftime("%Y-%m-%d %H:%M")
    state = load_state()
    state["total_score"] = state.get("total_score", 0) + 1
    state["checkins"].append({
        "time": datetime.now().strftime("%H:%M"),
        "event_type": "restroom",
        "exercise": None,
        "work_content": "Away / Restroom",
        "focus_minutes": 0,
        "score": 1,
    })
    save_state(state)
    _append_log(f"[{ns}] Event: Restroom | Focus Reset | +1 Point\n")
    _log("Away: timer reset, +1pt logged")


# ═════════════════════════════════════════════════════════════════════════════
#  EXERCISE SELECTION
# ═════════════════════════════════════════════════════════════════════════════
def pick_exercises(state: dict) -> list:
    all_exs   = load_exercises()
    completed = set(state.get("completed_exercises", []))
    counts    = state.get("category_counts", {})
    available = [e for e in all_exs if e["id"] not in completed] or list(all_exs)
    by_cat: dict = {}
    for ex in available:
        by_cat.setdefault(ex["category"], []).append(ex)
    deficits = [c for c, m in DAILY_MINIMUMS.items()
                if counts.get(c, 0) < m and by_cat.get(c)]
    result, used_ids, used_cats = [], set(), set()
    random.shuffle(deficits)
    for cat in deficits:
        pool = [e for e in by_cat.get(cat, []) if e["id"] not in used_ids]
        if pool:
            ex = random.choice(pool)
            result.append(ex); used_ids.add(ex["id"]); used_cats.add(cat)
        if len(result) == 3: break
    if len(result) < 3:
        for cat in [c for c in by_cat if c not in used_cats]:
            pool = [e for e in by_cat[cat] if e["id"] not in used_ids]
            if pool:
                ex = random.choice(pool)
                result.append(ex); used_ids.add(ex["id"]); used_cats.add(cat)
            if len(result) == 3: break
    if len(result) < 3:
        pool = [e for e in available if e["id"] not in used_ids]
        random.shuffle(pool)
        for ex in pool:
            result.append(ex)
            if len(result) == 3: break
    return result[:3]


# ═════════════════════════════════════════════════════════════════════════════
#  QUARTZ IDLE DETECTION
# ═════════════════════════════════════════════════════════════════════════════
def get_idle_seconds() -> float:
    try:
        import Quartz
        return float(Quartz.CGEventSourceSecondsSinceLastEventType(
            Quartz.kCGEventSourceStateHIDSystemState, 0xFFFFFFFF
        ))
    except Exception:
        return 0.0


# ═════════════════════════════════════════════════════════════════════════════
#  SMART ACTIVE TIMER LOOP
# ═════════════════════════════════════════════════════════════════════════════
def _active_timer_loop() -> None:
    """Background thread. Accumulates ACTIVE seconds; triggers breaks."""
    while True:
        time.sleep(1)
        snoozed_trigger = normal_trigger = show_warn = False

        with _lock:
            if _g["break_locked"]:
                continue

            # Away / paused — timer frozen until user logs return
            if _g.get("away_mode"):
                continue

            # End-of-day mode — reset automatically at midnight
            if _g["done_for_today"]:
                if _g["done_for_date"] != today_str():
                    _g["done_for_today"] = False
                    _g["done_for_date"]  = ""
                    _g["active_seconds"] = 0
                    _g["warning_shown"]  = False
                    _log("New day — end-of-day flag cleared")
                else:
                    continue

            # Snooze period
            if _g["snooze_until"] > 0:
                if time.time() >= _g["snooze_until"]:
                    _g["snooze_until"] = 0.0
                    _g["break_locked"] = True
                    snoozed_trigger = True
                continue  # don't accumulate during snooze

            # Idle check
            if get_idle_seconds() >= IDLE_THRESHOLD:
                continue

            # Accumulate
            _g["active_seconds"] += 1
            remaining = INTERVAL_SECONDS - _g["active_seconds"]

            if not _g["warning_shown"] and remaining <= WARNING_ADVANCE:
                _g["warning_shown"] = True
                show_warn = True

            if remaining <= 0:
                _g["active_seconds"] = 0
                _g["warning_shown"]  = False
                _g["snooze_available"] = True
                _g["break_locked"]   = True
                normal_trigger = True

        # Dispatch outside the lock
        if show_warn:
            show_warning()
        if snoozed_trigger:
            threading.Thread(target=lambda: show_kiosk(True), daemon=True).start()
        if normal_trigger:
            threading.Thread(target=lambda: show_kiosk(False), daemon=True).start()


# ═════════════════════════════════════════════════════════════════════════════
#  AWAY + SNOOZE
# ═════════════════════════════════════════════════════════════════════════════
def handle_restroom() -> None:
    """Quick restroom tap: reset timer, log event, skip exercise next break."""
    with _lock:
        _g["active_seconds"]   = 0
        _g["warning_shown"]    = False
        _g["snooze_until"]     = 0.0
        _g["break_locked"]     = False
        _g["snooze_available"] = True
        _g["skip_exercise"]    = True
        _g["last_checkin_ts"]  = time.time()
    close_warning()
    close_kiosk()
    _log_restroom_event()

def handle_away() -> None:
    """Back-compat alias → restroom."""
    handle_restroom()

def handle_pause() -> None:
    """Pause timer and show the full-screen away overlay."""
    with _lock:
        _g["away_mode"]      = True
        _g["away_start_ts"]  = time.time()
        _g["active_seconds"] = 0
        _g["warning_shown"]  = False
        _g["snooze_until"]   = 0.0
        _g["break_locked"]   = False
    close_warning()
    # Show break window in "away" mode — user sees elapsed timer and can log return
    url = f"http://localhost:{PORT}/?away=1"
    _dispatch("showBreakWindow:", url)
    _log("Paused — away overlay shown")

def handle_snooze() -> bool:
    with _lock:
        if not _g["snooze_available"]:
            return False
        _g["snooze_available"] = False
        _g["snooze_until"]     = time.time() + SNOOZE_DELAY
    return True

def handle_end_of_day() -> dict:
    """Stop breaks for today. Return today's summary."""
    with _lock:
        _g["done_for_today"] = True
        _g["done_for_date"]  = today_str()
        _g["active_seconds"] = 0
        _g["warning_shown"]  = False
        _g["snooze_until"]   = 0.0
        _g["break_locked"]   = False
    close_warning()
    close_kiosk()
    state = load_state()
    _archive_daily_state(state)
    _write_daily_summary(state)
    _log("End of day — breaks paused until midnight")
    return state

def handle_resume_day() -> None:
    """Re-enable breaks after end-of-day."""
    with _lock:
        _g["done_for_today"] = False
        _g["done_for_date"]  = ""
        _g["active_seconds"] = 0
        _g["warning_shown"]  = False
    _log("Breaks resumed")


# ═════════════════════════════════════════════════════════════════════════════
#  WINDOW CONTROLLER  (NSObject — all UI ops on main thread)
# ═════════════════════════════════════════════════════════════════════════════
class WindowController(NSObject):
    def init(self):
        self = objc.super(WindowController, self).init()
        if self is None: return None
        self._bw  = None   # NSWindow break window (primary — kept for compat)
        self._bwv = None   # WKWebView (break)
        self._bw_extra = []  # extra BreakWindow instances for secondary screens
        self._ww  = None   # NSWindow warning panel
        self._rw  = None   # NSWindow records panel
        self._si  = None   # NSStatusItem
        # Menu item refs (for language switching)
        self._si_hdr      = None
        self._si_timer    = None
        self._si_away     = None
        self._si_trig     = None
        self._si_rec      = None
        self._si_quit      = None
        self._si_eod       = None
        self._si_pause     = None   # "Pause Timer" / "I'm back"
        self._si_away_form = None
        self._waw          = None   # away-form / return-form window
        self._wp           = None   # preferences window
        self._lang_en_item = None
        self._si_prefs     = None
        return self

    # ── App delegate ──────────────────────────────────────────────────────────
    def applicationDidFinishLaunching_(self, _):
        _log("NSApplication ready.")
        self._setup_status_bar()
        # Listen for screen-wake so we can auto-show the return form
        ws_nc = NSWorkspace.sharedWorkspace().notificationCenter()
        ws_nc.addObserver_selector_name_object_(
            self, "screenDidWake:", "NSWorkspaceScreensDidWakeNotification", None)

    def applicationShouldTerminateAfterLastWindowClosed_(self, _):
        return False

    # _L is a module-level function (see below WindowController)

    # ── Status bar ────────────────────────────────────────────────────────────
    def _setup_status_bar(self):
        _log("Status bar: starting setup …")
        try:
            from AppKit import NSImage
            bar      = NSStatusBar.systemStatusBar()
            self._si = bar.statusItemWithLength_(NSVariableStatusItemLength)
            btn = self._si.button()
            _log(f"Status bar: statusItem created  btn={btn}")
            if btn is not None:
                try:
                    img = NSImage.imageWithSystemSymbolName_accessibilityDescription_(
                        "leaf.fill", "re.set")
                    if img is not None:
                        img.setTemplate_(True)
                        btn.setImage_(img)
                        _log("Status bar: SF Symbol leaf.fill applied")
                    else:
                        btn.setTitle_("🌿")
                except Exception as e:
                    btn.setTitle_("🌿")
                    _log(f"Status bar: SF Symbol failed ({e}), used emoji")
            else:
                self._si.setTitle_("🌿")
                _log("Status bar: used legacy setTitle_")
        except Exception as e:
            _log(f"Status bar: CRASHED — {e}"); return

        menu = NSMenu.alloc().init()

        def _item(title, action, key="", enabled=True, target=None):
            it = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, action, key)
            if not enabled: it.setEnabled_(False)
            if target: it.setTarget_(target)
            menu.addItem_(it)
            return it

        self._si_hdr   = _item(_L("app_title"), None, enabled=False)
        self._si_timer = _item("—", None, enabled=False)
        menu.addItem_(NSMenuItem.separatorItem())
        self._si_pause     = _item(_L("pause"),     "handlePause:",     target=self)
        self._si_away_form = _item(_L("away_form"), "handleAwayForm:",  target=self)
        self._si_trig      = _item(_L("trigger"),   "handleTrigger:",    target=self)
        menu.addItem_(NSMenuItem.separatorItem())
        self._si_rec   = _item(_L("records"), "handleViewRecords:", target=self)
        self._si_prefs = _item(_L("prefs"), "handlePreferences:", target=self)

        menu.addItem_(NSMenuItem.separatorItem())
        self._si_eod = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            self._eod_title(), "handleEndOfDay:", "")
        self._si_eod.setTarget_(self); menu.addItem_(self._si_eod)

        menu.addItem_(NSMenuItem.separatorItem())
        self._si_quit = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            _L("quit"), "terminate:", "q")
        self._si_quit.setTarget_(NSApp); menu.addItem_(self._si_quit)

        self._si.setMenu_(menu)
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            5.0, self, "updateStatusBar:", None, True)
        _log("Status bar: setup complete")

    def _update_menu_lang(self):
        """Refresh all menu item titles after a language change."""
        if self._si_hdr:       self._si_hdr.setTitle_(_L("app_title"))
        if self._si_pause:     self._si_pause.setTitle_(self._pause_title())
        if self._si_away_form: self._si_away_form.setTitle_(_L("away_form"))
        if self._si_trig:      self._si_trig.setTitle_(_L("trigger"))
        if self._si_rec:      self._si_rec.setTitle_(_L("records"))
        if self._si_prefs:    self._si_prefs.setTitle_(_L("prefs"))
        if self._si_quit:     self._si_quit.setTitle_(_L("quit"))
        if self._si_eod:
            self._si_eod.setTitle_(self._eod_title())

    # ── Menu action handlers ──────────────────────────────────────────────────
    def _pause_title(self):
        if _g.get("away_mode"):
            secs = int(time.time() - _g.get("away_start_ts", time.time()))
            m, s = secs // 60, secs % 60
            return _L("resume_log") + f"  ({m:02d}:{s:02d})"
        return _L("pause")

    def screenDidWake_(self, _):
        """Auto-show return form when screen wakes while in away mode."""
        if _g.get("away_mode"):
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                "showReturnForm:", None, False)

    def handlePause_(self, _):
        if _g.get("away_mode"):
            # Already paused → open return form
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                "showReturnForm:", None, False)
        else:
            threading.Thread(target=handle_pause, daemon=True).start()

    def showReturnForm_(self, _):
        pw, ph = 420.0, 360.0
        sw = NSScreen.mainScreen().frame().size.width
        sh = NSScreen.mainScreen().frame().size.height
        pf = NSMakeRect((sw - pw) / 2, (sh - ph) / 2, pw, ph)
        if not self._waw:
            mask = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
            self._waw = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                pf, mask, NSBackingStoreBuffered, False)
            self._waw.setReleasedWhenClosed_(False)
            self._waw.setLevel_(NSFloatingWindowLevel)
            self._waw.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
            cfg = WKWebViewConfiguration.alloc().init()
            wv  = WKWebView.alloc().initWithFrame_configuration_(
                NSMakeRect(0, 0, pw, ph), cfg)
            self._waw.setContentView_(wv)
        title = "re.set — 回来啦" if _g.get("lang","zh") == "zh" else "re.set — Welcome Back"
        self._waw.setTitle_(title)
        self._waw.contentView().loadRequest_(
            NSURLRequest.requestWithURL_(
                NSURL.URLWithString_(f"http://localhost:{PORT}/return-form")))
        self._waw.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def handleAwayForm_(self, _):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "showAwayForm:", None, False)

    def showAwayForm_(self, _):
        pw, ph = 420.0, 340.0
        sw = NSScreen.mainScreen().frame().size.width
        sh = NSScreen.mainScreen().frame().size.height
        pf = NSMakeRect((sw - pw) / 2, (sh - ph) / 2, pw, ph)
        if not self._waw:
            mask = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable)
            self._waw = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                pf, mask, NSBackingStoreBuffered, False)
            self._waw.setReleasedWhenClosed_(False)
            self._waw.setLevel_(NSFloatingWindowLevel)
            self._waw.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
            cfg = WKWebViewConfiguration.alloc().init()
            wv  = WKWebView.alloc().initWithFrame_configuration_(
                NSMakeRect(0, 0, pw, ph), cfg)
            self._waw.setContentView_(wv)
        title = "re.set — 记录工作时段" if _g.get("lang","zh") == "zh" else "re.set — Log Work Session"
        self._waw.setTitle_(title)
        self._waw.contentView().loadRequest_(
            NSURLRequest.requestWithURL_(
                NSURL.URLWithString_(f"http://localhost:{PORT}/away-form")))
        self._waw.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def handleTrigger_(self, _):
        threading.Thread(target=lambda: show_kiosk(False), daemon=True).start()

    def handleViewRecords_(self, _):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "showRecordsPanel:", None, False)

    def refreshAfterPrefs_(self, _):
        """Called on main thread after saving preferences from HTTP."""
        self._update_menu_lang()
        if self._rw and self._rw.isVisible():
            self._rw.contentView().loadRequest_(
                NSURLRequest.requestWithURL_(
                    NSURL.URLWithString_(f"http://localhost:{PORT}/records")))

    def handlePreferences_(self, _):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            "showPreferences:", None, False)

    def showPreferences_(self, _):
        pw, ph = 520.0, 560.0
        sw = NSScreen.mainScreen().frame().size.width
        sh = NSScreen.mainScreen().frame().size.height
        pf = NSMakeRect((sw - pw) / 2, (sh - ph) / 2, pw, ph)
        if not self._wp:
            mask = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable | NSWindowStyleMaskMiniaturizable)
            self._wp = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                pf, mask, NSBackingStoreBuffered, False)
            self._wp.setReleasedWhenClosed_(False)
            self._wp.setLevel_(NSFloatingWindowLevel)
            self._wp.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
            cfg = WKWebViewConfiguration.alloc().init()
            wv  = WKWebView.alloc().initWithFrame_configuration_(
                NSMakeRect(0, 0, pw, ph), cfg)
            self._wp.setContentView_(wv)
        title = "re.set — 设置" if _g.get("lang", "zh") == "zh" else "re.set — Preferences"
        self._wp.setTitle_(title)
        self._wp.contentView().loadRequest_(
            NSURLRequest.requestWithURL_(
                NSURL.URLWithString_(f"http://localhost:{PORT}/preferences")))
        self._wp.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def _eod_title(self):
        return _L("eod_off") if _g.get("done_for_today") else _L("eod_on")

    def handleEndOfDay_(self, _):
        if _g.get("done_for_today"):
            threading.Thread(target=handle_resume_day, daemon=True).start()
        else:
            threading.Thread(target=handle_end_of_day, daemon=True).start()
        # Update menu title on next timer tick
        if self._si_eod:
            self._si_eod.setTitle_(self._eod_title())

    def updateStatusBar_(self, _timer):
        if not self._si_timer: return
        rem  = max(0, INTERVAL_SECONDS - _g.get("active_seconds", 0))
        m, s = rem // 60, rem % 60
        if _g.get("snooze_until", 0) > 0:
            sr = max(0, int(_g["snooze_until"] - time.time()))
            title = _L("snooze_fmt")(sr // 60, sr % 60)
        else:
            title = _L("timer_fmt")(m, s)
        self._si_timer.setTitle_(title)
        if self._si_pause:
            self._si_pause.setTitle_(self._pause_title())
        if self._si_eod:
            self._si_eod.setTitle_(self._eod_title())

    # ── Records panel ─────────────────────────────────────────────────────────
    def showRecordsPanel_(self, _):
        pw, ph = 600.0, 680.0
        sw = NSScreen.mainScreen().frame().size.width
        sh = NSScreen.mainScreen().frame().size.height
        pf = NSMakeRect((sw - pw) / 2, (sh - ph) / 2, pw, ph)

        if not self._rw:
            mask = (NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
                    | NSWindowStyleMaskMiniaturizable | NSWindowStyleMaskResizable)
            self._rw = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                pf, mask, NSBackingStoreBuffered, False)
            self._rw.setReleasedWhenClosed_(False)   # keep object alive after close
            self._rw.setMinSize_(NSMakeRect(0, 0, 480, 400).size)
            self._rw.setLevel_(NSFloatingWindowLevel)
            self._rw.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)
            cfg = WKWebViewConfiguration.alloc().init()
            wv  = WKWebView.alloc().initWithFrame_configuration_(
                NSMakeRect(0, 0, pw, ph), cfg)
            self._rw.setContentView_(wv)

        title = "re.set — 今日记录" if _g.get("lang", "zh") == "zh" else "re.set — Today's Records"
        self._rw.setTitle_(title)
        # Always reload so content is fresh on every open
        self._rw.contentView().loadRequest_(
            NSURLRequest.requestWithURL_(
                NSURL.URLWithString_(f"http://localhost:{PORT}/records")))
        self._rw.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    # ── Break window ──────────────────────────────────────────────────────────
    def _make_break_window(self, frame):
        """Create one full-screen BreakWindow covering *frame*."""
        bw = BreakWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            frame, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False)
        bw.setLevel_(BREAK_WINDOW_LEVEL)
        bw.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorStationary
            | NSWindowCollectionBehaviorIgnoresCycle)
        bw.setDelegate_(self)
        bw.setBackgroundColor_(NSColor.colorWithRed_green_blue_alpha_(
            0.969, 0.969, 0.976, 1.0))
        cfg = WKWebViewConfiguration.alloc().init()
        bwv = WKWebView.alloc().initWithFrame_configuration_(frame, cfg)
        bw.setContentView_(bwv)
        return bw, bwv

    def _setupBreakWindow(self):
        if self._bw: return
        frame = NSScreen.mainScreen().frame()
        self._bw, self._bwv = self._make_break_window(frame)
        _log("Break window (primary) created.")

    def showBreakWindow_(self, url_str):
        self._setupBreakWindow()
        req = NSURLRequest.requestWithURL_(NSURL.URLWithString_(url_str))
        self._bwv.loadRequest_(req)
        self._bw.makeKeyAndOrderFront_(None)
        self._bw.makeFirstResponder_(self._bwv)
        NSApp.activateIgnoringOtherApps_(True)

        # Cover every additional screen with a black-out window (no interactive content)
        screens = list(NSScreen.screens() or [])
        main_fr = NSScreen.mainScreen().frame()
        for extra_bw in self._bw_extra:
            extra_bw.orderOut_(None)
        self._bw_extra = []
        for scr in screens:
            fr = scr.frame()
            # Skip the screen already covered by the primary window
            if (abs(fr.origin.x - main_fr.origin.x) < 1 and
                    abs(fr.origin.y - main_fr.origin.y) < 1):
                continue
            bw, bwv = self._make_break_window(fr)
            # Secondary screens show a blank overlay (no WKWebView content needed,
            # but we load the same URL so users can still interact if desired)
            bwv.loadRequest_(req)
            bw.makeKeyAndOrderFront_(None)
            self._bw_extra.append(bw)
        _log(f"Break window shown on {1+len(self._bw_extra)} screen(s) → {url_str}")

    def hideBreakWindow_(self, _):
        if self._bw:
            self._bw.orderOut_(None)
        for bw in self._bw_extra:
            bw.orderOut_(None)
        self._bw_extra = []
        _log("Break window(s) hidden.")

    def closeAuxWindow_(self, _):
        """Close the auxiliary popup (away form / return form)."""
        if self._waw: self._waw.orderOut_(None)

    def windowShouldClose_(self, _): return False

    # ── Warning panel ─────────────────────────────────────────────────────────
    def showWarningPanel_(self, _):
        sw = NSScreen.mainScreen().frame().size.width
        sh = NSScreen.mainScreen().frame().size.height
        pw, ph = 244.0, 96.0
        pf = NSMakeRect(sw - pw - 20, sh - ph - 20, pw, ph)
        if not self._ww:
            self._ww = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                pf, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, False)
            self._ww.setLevel_(NSStatusWindowLevel + 1)
            self._ww.setOpaque_(False)
            self._ww.setBackgroundColor_(NSColor.clearColor())
            self._ww.setHasShadow_(True)
            self._ww.setCollectionBehavior_(
                NSWindowCollectionBehaviorCanJoinAllSpaces
                | NSWindowCollectionBehaviorStationary)
            cfg = WKWebViewConfiguration.alloc().init()
            wv  = WKWebView.alloc().initWithFrame_configuration_(
                NSMakeRect(0, 0, pw, ph), cfg)
            self._ww.setContentView_(wv)
        self._ww.setFrame_display_(pf, False)
        self._ww.contentView().loadRequest_(
            NSURLRequest.requestWithURL_(
                NSURL.URLWithString_(f"http://localhost:{PORT}/warning")))
        self._ww.orderFront_(None)

    def hideWarningPanel_(self, _):
        if self._ww: self._ww.orderOut_(None)


# ═════════════════════════════════════════════════════════════════════════════
#  WINDOW API  (thread-safe dispatch to main thread)
# ═════════════════════════════════════════════════════════════════════════════
def _dispatch(sel: str, arg=None) -> None:
    if _wc is not None:
        _wc.performSelectorOnMainThread_withObject_waitUntilDone_(sel, arg, False)

def show_kiosk(snoozed: bool = False) -> None:
    _dispatch("hideWarningPanel:", None)
    url = f"http://localhost:{PORT}/" + ("?snoozed=true" if snoozed else "")
    _dispatch("showBreakWindow:", url)

def close_kiosk() -> None:
    _dispatch("hideBreakWindow:", None)

def show_warning() -> None:
    _dispatch("showWarningPanel:", None)

def close_warning() -> None:
    _dispatch("hideWarningPanel:", None)


# ═════════════════════════════════════════════════════════════════════════════
#  HTTP HANDLER
# ═════════════════════════════════════════════════════════════════════════════
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_): pass

    def _json(self, data, status=200):
        b = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers(); self.wfile.write(b)

    def _html(self, html, status=200):
        b = html.encode() if isinstance(html, str) else html
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers(); self.wfile.write(b)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        p = urlparse(self.path)
        r = {
            "/":              self._serve_ui,
            "":               self._serve_ui,
            "/records":       self._serve_records,
            "/away-form":     self._serve_away_form,
            "/return-form":   self._serve_return_form,
            "/warning":       self._serve_warning,
            "/shared.js":     self._serve_shared_js,
            "/api/status":    self._api_status,
            "/api/exercises": self._api_exercises,
            "/api/records":        self._api_records,
            "/api/config":         self._api_config,
            "/api/history/list":    self._api_history_list,
            "/api/activity-types":  self._api_activity_types_get,
            "/api/prefs":           self._api_prefs_get,
            "/preferences":         self._serve_preferences,
        }.get(p.path)
        if r:
            r()
        elif p.path == "/api/history/date":
            qs = parse_qs(p.query)
            self._api_history_date(qs.get("d", [today_str()])[0])
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        r = {
            "/api/checkin":      self._api_checkin,
            "/api/restroom":     self._api_restroom,
            "/api/away-checkin": self._api_away_checkin,
            "/api/close":      self._api_close,
            "/api/snooze":     self._api_snooze,
            "/api/trigger":    self._api_trigger,
            "/api/away":       self._api_away,
            "/api/pause":           self._api_pause,
            "/api/close-popup":     self._api_close_popup,
            "/api/return-log":      self._api_return_log,
            "/api/end-of-day":      self._api_end_of_day,
            "/api/activity-types":  self._api_activity_types_post,
            "/api/records/edit":    self._api_records_edit,
            "/api/records/delete":  self._api_records_delete,
            "/api/prefs":                self._api_prefs_post,
            "/api/postpone-warning":     self._api_postpone_warning,
        }.get(urlparse(self.path).path)
        if r: r()
        else: self.send_response(404); self.end_headers()


    def _serve_ui(self):
        try:   self._html(UI_FILE.read_bytes())
        except Exception as e: self._html(f"<pre>Error: {e}</pre>", 500)

    def _serve_records(self):
        try:   self._html(RECORDS_UI_FILE.read_bytes())
        except Exception as e: self._html(f"<pre>Error: {e}</pre>", 500)

    def _serve_preferences(self):
        try:   self._html(PREFERENCES_UI_FILE.read_bytes())
        except Exception as e: self._html(f"<pre>Error: {e}</pre>", 500)

    def _serve_warning(self):
        try:
            self._html(WARNING_FILE.read_bytes())
        except Exception as e:
            self._html(f"<pre>Error: {e}</pre>", 500)

    def _serve_shared_js(self):
        try:
            b = SHARED_JS_FILE.read_bytes()
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            err = str(e).encode()
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/javascript; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b)

    def _api_config(self):
        cfg = dict(load_config())
        cfg["daily_minimums"] = DAILY_MINIMUMS
        cfg["eye_timer_seconds"] = EYE_TIMER_SECONDS
        cfg["warning_advance_seconds"] = WARNING_ADVANCE
        cfg["idle_threshold_seconds"] = IDLE_THRESHOLD
        self._json(cfg)

    def _api_prefs_get(self):
        self._json({
            "interval_minutes": INTERVAL_SECONDS // 60,
            "lang":             _g.get("lang", "zh"),
            "interval_presets": list(INTERVAL_PRESETS),
            "activity_types":   load_activity_types(),
        })

    def _api_prefs_post(self):
        body = self._body()
        if "interval_minutes" in body:
            try:
                apply_interval_minutes(int(body["interval_minutes"]))
            except (TypeError, ValueError):
                pass
        if "lang" in body:
            apply_language(str(body["lang"]))
        if "activity_types" in body and isinstance(body["activity_types"], list):
            cleaned = []
            for tp in body["activity_types"]:
                if isinstance(tp, dict) and tp.get("id") and tp.get("label") and tp.get("color"):
                    try:
                        w = float(tp.get("weight", 1.0))
                    except (TypeError, ValueError):
                        w = 1.0
                    w = max(0.1, min(3.0, w))
                    cleaned.append({"id": str(tp["id"]), "label": str(tp["label"]),
                                     "color": str(tp["color"]), "weight": w})
            if cleaned:
                save_activity_types(cleaned)
        self._json({"success": True})
        if _wc is not None:
            _wc.performSelectorOnMainThread_withObject_waitUntilDone_(
                "refreshAfterPrefs:", None, False)

    def _api_records(self):
        state  = load_state()
        counts = state.get("category_counts", {})
        self._json({
            "date":            state.get("date"),
            "checkins":        state.get("checkins", []),
            "total_score":     state.get("total_score", 0),
            "focus_minutes":   state.get("focus_minutes", 0),
            "category_counts": counts,
            "daily_minimums":  DAILY_MINIMUMS,
            "all_minimums_met": all(
                counts.get(c, 0) >= m for c, m in DAILY_MINIMUMS.items()),
            "lang":            _g.get("lang", "zh"),
            "done_for_today":  _g.get("done_for_today", False),
        })

    def _api_records_edit(self):
        body     = self._body()
        date_str = body.get("date", today_str())
        try:
            idx = int(body.get("index", -1))
        except (TypeError, ValueError):
            self.send_response(400); self.end_headers(); return

        # Load the right data source
        if date_str == today_str():
            state    = load_state()
            is_today = True
        else:
            p = HISTORY_DIR / f"{date_str}.json"
            if not p.exists():
                self._json({"success": False, "error": "date not found"}); return
            try:
                state = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                self._json({"success": False, "error": "corrupt history"}); return
            is_today = False

        ckins = state.get("checkins", [])
        if idx < 0 or idx >= len(ckins):
            self._json({"success": False, "error": "index out of range"}); return

        if "time" in body:
            ckins[idx]["time"] = str(body["time"])[:5]
        if "start_time" in body:
            v = body["start_time"]
            ckins[idx]["start_time"] = str(v)[:5] if v else None
        if "end_time" in body:
            v = body["end_time"]
            ckins[idx]["end_time"] = str(v)[:5] if v else None
        if "work_content" in body:
            ckins[idx]["work_content"] = str(body["work_content"])
        if "activity_type" in body:
            ckins[idx]["activity_type"] = body["activity_type"] or None
        if "focus_minutes" in body:
            try:
                new_fm = max(0, int(body["focus_minutes"]))
                old_fm = ckins[idx].get("focus_minutes", 0) or 0
                # Update the day's total focus_minutes accordingly
                state["focus_minutes"] = max(0,
                    state.get("focus_minutes", 0) - old_fm + new_fm)
                ckins[idx]["focus_minutes"] = new_fm
            except (TypeError, ValueError):
                pass

        state["checkins"] = ckins
        if is_today:
            save_state(state)
        else:
            p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

        _log(f"Record edit: date={date_str} idx={idx}")
        self._json({"success": True})

    def _api_records_delete(self):
        body     = self._body()
        date_str = body.get("date", today_str())
        try:
            idx = int(body.get("index", -1))
        except (TypeError, ValueError):
            self.send_response(400); self.end_headers(); return
        if date_str == today_str():
            state    = load_state()
            is_today = True
        else:
            p = HISTORY_DIR / f"{date_str}.json"
            if not p.exists():
                self._json({"success": False, "error": "date not found"}); return
            try:
                state = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                self._json({"success": False, "error": "corrupt history"}); return
            is_today = False
        ckins = state.get("checkins", [])
        if idx < 0 or idx >= len(ckins):
            self._json({"success": False, "error": "index out of range"}); return
        removed = ckins.pop(idx)
        state["total_score"] = max(0, state.get("total_score", 0) - (removed.get("score") or 0))
        state["focus_minutes"] = max(0, state.get("focus_minutes", 0) - (removed.get("focus_minutes") or 0))
        state["checkins"] = ckins
        if is_today:
            save_state(state)
        else:
            p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        _log(f"Record deleted: date={date_str} idx={idx}")
        self._json({"success": True})

    def _api_activity_types_get(self):
        self._json(load_activity_types())

    def _api_activity_types_post(self):
        types = self._body()
        if not isinstance(types, list):
            self.send_response(400); self.end_headers(); return
        # Basic validation: each entry must have id, label, color
        cleaned = []
        for tp in types:
            if isinstance(tp, dict) and tp.get("id") and tp.get("label") and tp.get("color"):
                try:
                    w = float(tp.get("weight", 1.0))
                except (TypeError, ValueError):
                    w = 1.0
                w = max(0.1, min(3.0, w))
                cleaned.append({"id": str(tp["id"]), "label": str(tp["label"]),
                                 "color": str(tp["color"]), "weight": w})
        save_activity_types(cleaned)
        self._json({"success": True, "count": len(cleaned)})

    def _api_history_list(self):
        HISTORY_DIR.mkdir(exist_ok=True)
        result = {}
        for f in HISTORY_DIR.glob("*.json"):
            try:
                d = json.loads(f.read_text())
                result[f.stem] = {
                    "total_score":  d.get("total_score", 0),
                    "focus_minutes": d.get("focus_minutes", 0),
                    "checkins":     len(d.get("checkins", [])),
                }
            except Exception:
                pass
        # include today
        today = load_state()
        result[today_str()] = {
            "total_score":   today.get("total_score", 0),
            "focus_minutes": today.get("focus_minutes", 0),
            "checkins":      len(today.get("checkins", [])),
        }
        self._json(result)

    def _api_history_date(self, date_str: str):
        if date_str == today_str():
            return self._api_records()
        p = HISTORY_DIR / f"{date_str}.json"
        if p.exists():
            try:
                d = json.loads(p.read_text())
                d["lang"] = _g.get("lang", "zh")
                return self._json(d)
            except Exception:
                pass
        self._json({
            "date": date_str, "checkins": [], "total_score": 0,
            "focus_minutes": 0, "category_counts": {},
            "daily_minimums": DAILY_MINIMUMS, "all_minimums_met": False,
            "lang": _g.get("lang", "zh"),
        })

    def _api_end_of_day(self):
        if _g.get("done_for_today"):
            handle_resume_day()
            self._json({"success": True, "done": False})
        else:
            state = handle_end_of_day()
            self._json({"success": True, "done": True,
                        "total_score": state.get("total_score", 0)})

    def _api_status(self):
        state   = load_state()
        counts  = state.get("category_counts", {})
        all_met = all(counts.get(c,0) >= m for c,m in DAILY_MINIMUMS.items())
        rem     = max(0, INTERVAL_SECONDS - _g["active_seconds"])
        # Suggested focus = now minus end-time of the last recorded session.
        # Use the stored HH:MM from the last checkin record (robust across restarts).
        elapsed_min = 0
        ckins = state.get("checkins", [])
        if ckins:
            last_time_str = ckins[-1].get("time", "")
            try:
                lh, lm = map(int, last_time_str.split(":"))
                now_dt = datetime.now()
                last_dt = now_dt.replace(hour=lh, minute=lm, second=0, microsecond=0)
                diff = (now_dt - last_dt).total_seconds()
                if diff < 0:          # past midnight edge case
                    diff += 86400
                elapsed_min = max(0, int(diff / 60))
            except Exception:
                pass
        self._json({**state,
            "daily_minimums":         DAILY_MINIMUMS,
            "all_minimums_met":       all_met,
            "snooze_available":       _g["snooze_available"],
            "active_seconds":         _g["active_seconds"],
            "time_remaining_seconds": rem,
            "suggested_focus_minutes": elapsed_min,
            "skip_exercise":          _g.get("skip_exercise", False),
            "away_mode":              _g.get("away_mode", False),
            "away_seconds":           int(time.time() - _g.get("away_start_ts", time.time()))
                                      if _g.get("away_mode") else 0,
        })

    def _api_exercises(self):
        self._json(pick_exercises(load_state()))

    def _api_checkin(self):
        body = self._body()
        with _lock:
            state        = load_state()
            fm           = max(0, int(body.get("focus_minutes", 30)))
            wc           = str(body.get("work_content", "")).strip()
            ex           = body.get("exercise")
            act_type     = body.get("activity_type") or None
            fs           = activity_focus_score_points(fm, act_type)
            xs           = ex["score"] if ex else 0
            ss           = fs + xs

            if ex:
                eid = ex.get("id","")
                if eid not in state["completed_exercises"]:
                    state["completed_exercises"].append(eid)
                cat = ex.get("category","")
                state["category_counts"][cat] = state["category_counts"].get(cat,0) + 1

            state["total_score"]   = state.get("total_score",0) + ss
            state["focus_minutes"] = state.get("focus_minutes",0) + fm
            rec = {"time": datetime.now().strftime("%H:%M"),
                   "exercise": ex, "work_content": wc,
                   "focus_minutes": fm, "score": ss,
                   "activity_type": act_type}
            state["checkins"].append(rec)
            save_state(state)
            write_log_entry(state, rec)

            # Reset active timer for next cycle (window still showing)
            _g["active_seconds"]   = 0
            _g["warning_shown"]    = False
            _g["snooze_available"] = True
            _g["last_checkin_ts"]  = time.time()
            _g["skip_exercise"]    = False
            _g["away_mode"]        = False
            _g["away_start_ts"]    = 0.0
            _g["postpone_count"]   = 0

        _log(f"Checkin: +{ss}pts  total={state['total_score']}")
        self._json({"success": True, "session_score": ss,
                    "total_score": state["total_score"],
                    "focus_score": fs, "exercise_score": xs})

    def _api_close(self):
        body      = self._body()
        emergency = body.get("emergency", False)
        self._json({"success": True})
        def _do():
            time.sleep(0.2)
            with _lock:
                _g["break_locked"] = False
                if emergency:
                    _g["active_seconds"] = 0   # fresh timer after escape
            close_kiosk()
        threading.Thread(target=_do, daemon=True).start()

    def _api_snooze(self):
        ok = handle_snooze()
        self._json({"success": ok})
        if ok:
            def _do():
                time.sleep(0.2)
                with _lock: _g["break_locked"] = False
                close_kiosk()
            threading.Thread(target=_do, daemon=True).start()

    def _api_postpone_warning(self):
        """Postpone the upcoming break from the warning widget (max 3 times)."""
        POSTPONE_SECONDS = 5 * 60   # 5 minutes per tap
        MAX_POSTPONES    = 3
        with _lock:
            count = _g.get("postpone_count", 0)
            if count >= MAX_POSTPONES:
                self._json({"success": False, "reason": "max_postpones"})
                return
            _g["postpone_count"]  = count + 1
            _g["active_seconds"]  = max(0, _g["active_seconds"] - POSTPONE_SECONDS)
            _g["warning_shown"]   = False   # re-arm so warning re-fires when due again
        close_warning()
        _log(f"Warning postponed ({count+1}/{MAX_POSTPONES})")
        self._json({"success": True, "postpones_used": count + 1, "max": MAX_POSTPONES})

    def _api_trigger(self):
        threading.Thread(target=lambda: show_kiosk(False), daemon=True).start()
        self._json({"success": True})

    def _api_away(self):
        """Back-compat: /api/away now maps to restroom."""
        self._json({"success": True})
        threading.Thread(target=lambda: (time.sleep(0.2), handle_restroom()), daemon=True).start()

    def _api_restroom(self):
        self._json({"success": True})
        threading.Thread(target=lambda: (time.sleep(0.2), handle_restroom()), daemon=True).start()

    def _serve_away_form(self):
        try:    self._html(AWAY_FORM_FILE.read_bytes())
        except Exception as e: self._html(f"<pre>Error: {e}</pre>", 500)

    def _serve_return_form(self):
        try:    self._html(RETURN_FORM_FILE.read_bytes())
        except Exception as e: self._html(f"<pre>Error: {e}</pre>", 500)

    def _api_pause(self):
        self._json({"success": True})
        threading.Thread(target=handle_pause, daemon=True).start()

    def _api_close_popup(self):
        self._json({"success": True})
        _dispatch("closeAuxWindow:", None)

    def _api_return_log(self):
        body     = self._body()
        act_type = body.get("activity_type") or None
        wc       = str(body.get("work_content", "")).strip()
        with _lock:
            away_secs = int(time.time() - _g.get("away_start_ts", time.time()))
            fm = max(0, away_secs // 60)
            _g["away_mode"]      = False
            _g["away_start_ts"]  = 0.0
            _g["skip_exercise"]  = (act_type == "restroom")
            _g["last_checkin_ts"] = time.time()
            _g["active_seconds"] = 0
            _g["warning_shown"]  = False
            _g["snooze_available"] = True
        state = load_state()
        rec = {"time": datetime.now().strftime("%H:%M"),
               "exercise": None, "work_content": wc,
               "focus_minutes": fm, "score": 1,
               "activity_type": act_type, "event_type": "away_return"}
        state["total_score"]   = state.get("total_score", 0) + 1
        state["focus_minutes"] = state.get("focus_minutes", 0) + fm
        state["checkins"].append(rec)
        save_state(state)
        write_log_entry(state, rec)
        _log(f"Return log: {act_type}, {fm}min")
        self._json({"success": True, "away_minutes": fm})
        close_kiosk()  # close the away overlay

    def _api_away_checkin(self):
        """Log a work session from the away-form (no exercise)."""
        body     = self._body()
        fm       = max(0, int(body.get("focus_minutes", 0)))
        wc       = str(body.get("work_content", "")).strip()
        act_type = body.get("activity_type") or None
        with _lock:
            state = load_state()
            fs    = activity_focus_score_points(fm, act_type)
            rec   = {"time": datetime.now().strftime("%H:%M"),
                     "exercise": None, "work_content": wc,
                     "focus_minutes": fm, "score": fs,
                     "activity_type": act_type,
                     "event_type": "away_session"}
            state["total_score"]   = state.get("total_score", 0) + fs
            state["focus_minutes"] = state.get("focus_minutes", 0) + fm
            state["checkins"].append(rec)
            save_state(state)
            write_log_entry(state, rec)
            _g["active_seconds"]  = 0
            _g["warning_shown"]   = False
            _g["snooze_available"] = True
            _g["last_checkin_ts"] = time.time()
            _g["skip_exercise"]   = False
        _log(f"Away-checkin: +{fs}pts  wc='{wc}'  fm={fm}")
        self._json({"success": True, "score": fs, "total_score": state["total_score"]})


class _ThreadedServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════════
def _is_already_running() -> bool:
    """Return True if another instance is already listening on PORT."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        result = s.connect_ex(("127.0.0.1", PORT))
        s.close()
        return result == 0
    except Exception:
        return False


def main() -> None:
    global _wc, INTERVAL_SECONDS

    # Single-instance guard — if already running, exit silently
    if _is_already_running():
        _log("Already running — exiting duplicate instance.")
        sys.exit(0)

    # Restore saved settings from config
    cfg = load_config()
    saved_mins = cfg.get("interval_minutes", 30)
    if saved_mins in INTERVAL_PRESETS:
        INTERVAL_SECONDS = saved_mins * 60
    _g["lang"] = cfg.get("lang", "zh")
    _log(f"Config loaded: interval={INTERVAL_SECONDS//60}min  lang={_g['lang']}")

    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)

    _wc = WindowController.alloc().init()
    app.setDelegate_(_wc)

    # HTTP server
    def _srv():
        s = _ThreadedServer(("0.0.0.0", PORT), Handler)
        _log(f"HTTP on 0.0.0.0:{PORT}")
        s.serve_forever()
    threading.Thread(target=_srv, daemon=True).start()

    # Smart active timer
    threading.Thread(target=_active_timer_loop, daemon=True).start()
    _log(f"Smart timer started  idle_threshold={IDLE_THRESHOLD}s  interval={INTERVAL_SECONDS//60}min")

    app.run()


if __name__ == "__main__":
    main()
