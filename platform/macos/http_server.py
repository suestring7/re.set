from __future__ import annotations
import http.server
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from core.models.app_config import (
    DAILY_MINIMUMS, EYE_TIMER_SECONDS, IDLE_THRESHOLD,
    PORT, WARNING_ADVANCE,
)
from core.models.checkin import CheckIn
from core.services.scoring import focus_score
from core.utils.date_helpers import now_hhmm, today_str
from core.viewmodels.app_viewmodel import AppViewModel
from core.viewmodels.preferences_viewmodel import PreferencesViewModel
from core.viewmodels.records_viewmodel import RecordsViewModel
from core.services.exercise_service import ExerciseService


def make_handler(
    app_vm: AppViewModel,
    records_vm: RecordsViewModel,
    prefs_vm: PreferencesViewModel,
    exercise_svc: ExerciseService,
    resource_dir: Path,
    dispatch_fn,
) -> type:

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *_): pass

        def _json(self, data, status: int = 200) -> None:
            b = json.dumps(data, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b)

        def _html(self, html, status: int = 200) -> None:
            b = html.encode() if isinstance(html, str) else html
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length", 0))
            return json.loads(self.rfile.read(n)) if n else {}

        def _serve_file(self, name: str) -> None:
            try:
                self._html((resource_dir / name).read_bytes())
            except Exception as e:
                self._html(f"<pre>Error: {e}</pre>", 500)

        def do_OPTIONS(self) -> None:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self) -> None:
            p = urlparse(self.path)
            routes = {
                "/":                    lambda: self._serve_file("break_reminder_ui.html"),
                "":                     lambda: self._serve_file("break_reminder_ui.html"),
                "/records":             lambda: self._serve_file("records_ui.html"),
                "/away-form":           lambda: self._serve_file("away_form.html"),
                "/return-form":         lambda: self._serve_file("return_form.html"),
                "/warning":             lambda: self._serve_file("warning.html"),
                "/preferences":         lambda: self._serve_file("preferences.html"),
                "/shared.js":           self._serve_shared_js,
                "/api/status":          self._api_status,
                "/api/exercises":       self._api_exercises,
                "/api/records":         self._api_records,
                "/api/config":          self._api_config,
                "/api/history/list":    self._api_history_list,
                "/api/activity-types":  self._api_activity_types_get,
                "/api/prefs":           self._api_prefs_get,
            }
            handler = routes.get(p.path)
            if handler:
                handler()
            elif p.path == "/api/history/date":
                qs = parse_qs(p.query)
                self._api_history_date(qs.get("d", [today_str()])[0])
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self) -> None:
            routes = {
                "/api/checkin":              self._api_checkin,
                "/api/away-checkin":         self._api_away_checkin,
                "/api/return-log":           self._api_return_log,
                "/api/close":                self._api_close,
                "/api/close-popup":          self._api_close_popup,
                "/api/snooze":               self._api_snooze,
                "/api/trigger":              self._api_trigger,
                "/api/away":                 self._api_away,
                "/api/restroom":             self._api_restroom,
                "/api/pause":                self._api_pause,
                "/api/end-of-day":           self._api_end_of_day,
                "/api/activity-types":       self._api_activity_types_post,
                "/api/records/edit":         self._api_records_edit,
                "/api/records/delete":       self._api_records_delete,
                "/api/prefs":                self._api_prefs_post,
                "/api/postpone-warning":     self._api_postpone_warning,
            }
            handler = routes.get(urlparse(self.path).path)
            if handler:
                handler()
            else:
                self.send_response(404)
                self.end_headers()

        # ── Static file helpers ───────────────────────────────────────────────

        def _serve_shared_js(self) -> None:
            try:
                b = (resource_dir / "shared.js").read_bytes()
            except Exception as e:
                b = str(e).encode()
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b)

        # ── GET handlers ──────────────────────────────────────────────────────

        def _api_config(self) -> None:
            from core.services.persistence import PersistenceService
            self._json({
                "daily_minimums":          DAILY_MINIMUMS,
                "eye_timer_seconds":       EYE_TIMER_SECONDS,
                "warning_advance_seconds": WARNING_ADVANCE,
                "idle_threshold_seconds":  IDLE_THRESHOLD,
            })

        def _api_status(self) -> None:
            self._json(app_vm.get_status_dict())

        def _api_exercises(self) -> None:
            record = app_vm.today_record.value
            exs = exercise_svc.pick_exercises(record)
            self._json([e.to_dict() for e in exs])

        def _api_records(self) -> None:
            record = app_vm.today_record.value
            counts = record.category_counts
            from core.services.scoring import all_minimums_met
            self._json({
                **record.to_dict(),
                "daily_minimums":   DAILY_MINIMUMS,
                "all_minimums_met": all_minimums_met(counts),
                "lang":             app_vm.lang,
                "done_for_today":   app_vm.is_end_of_day.value,
            })

        def _api_prefs_get(self) -> None:
            self._json(prefs_vm.get_prefs())

        def _api_activity_types_get(self) -> None:
            self._json([t.to_dict() for t in prefs_vm.load_activity_types()])

        def _api_history_list(self) -> None:
            result = records_vm.load_history_list()
            # Always include today
            today = app_vm.today_record.value
            result[today_str()] = {
                "total_score":   today.total_score,
                "focus_minutes": today.focus_minutes,
                "checkins":      len(today.checkins),
            }
            self._json(result)

        def _api_history_date(self, date_str: str) -> None:
            if date_str == today_str():
                return self._api_records()
            record = records_vm.load_date(date_str)
            if record:
                d = record.to_dict()
                d["lang"] = app_vm.lang
                d["daily_minimums"] = DAILY_MINIMUMS
                from core.services.scoring import all_minimums_met
                d["all_minimums_met"] = all_minimums_met(record.category_counts)
                self._json(d)
            else:
                self._json({
                    "date": date_str, "checkins": [], "total_score": 0,
                    "focus_minutes": 0, "category_counts": {},
                    "daily_minimums": DAILY_MINIMUMS, "all_minimums_met": False,
                    "lang": app_vm.lang,
                })

        # ── POST handlers ─────────────────────────────────────────────────────

        def _lookup_act(self, act_id: str | None):
            if not act_id:
                return None
            for t in prefs_vm.load_activity_types():
                if t.id == act_id:
                    return t
            return None

        def _api_checkin(self) -> None:
            body     = self._body()
            fm       = max(0, int(body.get("focus_minutes", 30)))
            wc       = str(body.get("work_content", "")).strip()
            ex       = body.get("exercise")
            act_id   = body.get("activity_type") or None
            act      = self._lookup_act(act_id)
            fs       = focus_score(fm, act)
            xs       = ex["score"] if ex else 0
            checkin  = CheckIn(
                time=now_hhmm(), focus_minutes=fm, score=fs + xs,
                exercise=ex, work_content=wc, activity_type=act_id,
            )
            app_vm.commit_checkin(checkin)
            record = app_vm.today_record.value
            self._json({
                "success": True,
                "session_score": checkin.score,
                "total_score":   record.total_score,
                "focus_score":   fs,
                "exercise_score": xs,
            })

        def _api_away_checkin(self) -> None:
            body   = self._body()
            fm     = max(0, int(body.get("focus_minutes", 0)))
            wc     = str(body.get("work_content", "")).strip()
            act_id = body.get("activity_type") or None
            act    = self._lookup_act(act_id)
            fs     = focus_score(fm, act)
            checkin = CheckIn(
                time=now_hhmm(), focus_minutes=fm, score=fs,
                work_content=wc, activity_type=act_id, event_type="away_session",
            )
            app_vm.commit_away_checkin(checkin)
            record = app_vm.today_record.value
            self._json({"success": True, "score": fs, "total_score": record.total_score})

        def _api_return_log(self) -> None:
            body     = self._body()
            act_id   = body.get("activity_type") or None
            wc       = str(body.get("work_content", "")).strip()
            before   = body.get("before_leave")

            # Exit away mode and get elapsed seconds
            away_secs = app_vm.resume_from_away()
            fm = max(0, away_secs // 60)

            before_checkin = None
            if before and isinstance(before, dict):
                bl_fm   = max(0, int(before.get("focus_minutes", 0) or 0))
                bl_wc   = str(before.get("work_content", "")).strip()
                bl_id   = before.get("activity_type") or None
                bl_act  = self._lookup_act(bl_id)
                bl_fs   = focus_score(bl_fm, bl_act)
                before_checkin = CheckIn(
                    time=now_hhmm(), focus_minutes=bl_fm, score=bl_fs,
                    work_content=bl_wc, activity_type=bl_id, event_type="before_leave",
                )

            away_checkin = CheckIn(
                time=now_hhmm(), focus_minutes=fm, score=1,
                work_content=wc, activity_type=act_id, event_type="away_return",
            )
            app_vm.commit_return_log(before_checkin, away_checkin)
            self._json({"success": True, "away_minutes": fm})
            dispatch_fn("hideBreakWindow:", None)

        def _api_close(self) -> None:
            body      = self._body()
            emergency = body.get("emergency", False)
            self._json({"success": True})
            def _do():
                time.sleep(0.2)
                app_vm.release_break_lock(reset_active=bool(emergency))
                dispatch_fn("hideBreakWindow:", None)
            threading.Thread(target=_do, daemon=True).start()

        def _api_close_popup(self) -> None:
            self._json({"success": True})
            dispatch_fn("closeAuxWindow:", None)

        def _api_snooze(self) -> None:
            ok = app_vm.snooze()
            self._json({"success": ok})
            if ok:
                def _do():
                    time.sleep(0.2)
                    app_vm.release_break_lock()
                    dispatch_fn("hideBreakWindow:", None)
                threading.Thread(target=_do, daemon=True).start()

        def _api_postpone_warning(self) -> None:
            result = app_vm.postpone_warning()
            if result.get("success"):
                dispatch_fn("hideWarningPanel:", None)
            self._json(result)

        def _api_trigger(self) -> None:
            app_vm.trigger_break_now()
            self._json({"success": True})

        def _api_pause(self) -> None:
            app_vm.pause_timer()
            self._json({"success": True})
            url = f"http://localhost:{PORT}/?away=1"
            dispatch_fn("showBreakWindow:", url)

        def _api_away(self) -> None:
            self._json({"success": True})
            threading.Thread(
                target=lambda: (time.sleep(0.2), self._do_restroom()),
                daemon=True,
            ).start()

        def _api_restroom(self) -> None:
            self._json({"success": True})
            threading.Thread(
                target=lambda: (time.sleep(0.2), self._do_restroom()),
                daemon=True,
            ).start()

        def _do_restroom(self) -> None:
            record = app_vm.today_record.value
            checkin = CheckIn(
                time=now_hhmm(), focus_minutes=0, score=1,
                work_content="Away / Restroom", activity_type="restroom",
                event_type="restroom",
            )
            app_vm.commit_away_checkin(checkin)
            app_vm.release_break_lock()
            dispatch_fn("hideWarningPanel:", None)
            dispatch_fn("hideBreakWindow:", None)

        def _api_end_of_day(self) -> None:
            new_state = app_vm.toggle_end_of_day()
            record = app_vm.today_record.value
            dispatch_fn("updateMenuAfterPrefs:", None)
            self._json({
                "success": True,
                "done": new_state,
                "total_score": record.total_score,
            })

        def _api_prefs_post(self) -> None:
            body = self._body()
            if "interval_minutes" in body:
                try:
                    app_vm.update_interval(int(body["interval_minutes"]))
                except (TypeError, ValueError):
                    pass
            if "lang" in body:
                app_vm.update_lang(str(body["lang"]))
            if "activity_types" in body and isinstance(body["activity_types"], list):
                prefs_vm.save_activity_types(body["activity_types"])
            self._json({"success": True})
            dispatch_fn("updateMenuAfterPrefs:", None)

        def _api_activity_types_post(self) -> None:
            types = self._body()
            if not isinstance(types, list):
                self.send_response(400)
                self.end_headers()
                return
            count = prefs_vm.save_activity_types(types)
            self._json({"success": True, "count": count})

        def _api_records_edit(self) -> None:
            body     = self._body()
            date_str = body.get("date", today_str())
            try:
                idx = int(body.get("index", -1))
            except (TypeError, ValueError):
                self.send_response(400)
                self.end_headers()
                return
            updates = {k: body[k] for k in (
                "time", "start_time", "end_time",
                "work_content", "activity_type", "focus_minutes",
            ) if k in body}
            ok = records_vm.edit_checkin(date_str, idx, updates)
            if ok and date_str == today_str():
                app_vm.today_record.value = records_vm.load_today()
            self._json({"success": ok})

        def _api_records_delete(self) -> None:
            body     = self._body()
            date_str = body.get("date", today_str())
            try:
                idx = int(body.get("index", -1))
            except (TypeError, ValueError):
                self.send_response(400)
                self.end_headers()
                return
            ok = records_vm.delete_checkin(date_str, idx)
            if ok and date_str == today_str():
                app_vm.today_record.value = records_vm.load_today()
            self._json({"success": ok})

    return Handler


class _ThreadedServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True


def create_server(
    port: int,
    app_vm: AppViewModel,
    records_vm: RecordsViewModel,
    prefs_vm: PreferencesViewModel,
    exercise_svc: ExerciseService,
    resource_dir: Path,
    dispatch_fn,
) -> _ThreadedServer:
    handler = make_handler(
        app_vm=app_vm,
        records_vm=records_vm,
        prefs_vm=prefs_vm,
        exercise_svc=exercise_svc,
        resource_dir=resource_dir,
        dispatch_fn=dispatch_fn,
    )
    return _ThreadedServer(("0.0.0.0", port), handler)
