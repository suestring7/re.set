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
    PORT,
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
                "/plan-today":          lambda: self._serve_file("plan_today.html"),
                "/custom-alert":        lambda: self._serve_custom_alert(p.query),
                "/shared.js":           self._serve_shared_js,
                "/theme.css":           lambda: self._serve_css("theme.css"),
                "/api/status":             self._api_status,
                "/api/exercises":          self._api_exercises,
                "/api/exercises/library":  self._api_exercises_library_get,
                "/api/records":            self._api_records,
                "/api/config":             self._api_config,
                "/api/history/list":       self._api_history_list,
                "/api/muscle-stats":       self._api_muscle_stats,
                "/api/exercise-stats":     self._api_exercise_stats,
                "/api/restroom-stats":     self._api_restroom_stats,
                "/api/alerts":             self._api_alerts_get,
                "/api/activity-types":     self._api_activity_types_get,
                "/api/prefs":              self._api_prefs_get,
                "/api/export":             lambda: self._api_export(p.query),
            }
            handler = routes.get(p.path)
            if handler:
                handler()
            elif p.path == "/api/history/date":
                qs = parse_qs(p.query)
                self._api_history_date(qs.get("d", [today_str()])[0])
            elif p.path.startswith("/exercises/img/"):
                self._serve_exercise_img(p.path)
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
                "/api/records/add":          self._api_records_add,
                "/api/records/edit":         self._api_records_edit,
                "/api/records/delete":       self._api_records_delete,
                "/api/prefs":                self._api_prefs_post,
                "/api/reset-data":           self._api_reset_data,
                "/api/postpone-warning":     self._api_postpone_warning,
                "/api/plan/save":            self._api_plan_save,
                "/api/exercises/library":    self._api_exercises_library_post,
                "/api/alerts":               self._api_alerts_post,
            }
            handler = routes.get(urlparse(self.path).path)
            if handler:
                handler()
            else:
                self.send_response(404)
                self.end_headers()

        # ── Static file helpers ───────────────────────────────────────────────

        def _serve_css(self, name: str) -> None:
            try:
                b = (resource_dir / name).read_bytes()
            except Exception as e:
                msg = f"/* Error: {e} */".encode()
                self.send_response(500)
                self.send_header("Content-Type", "text/css; charset=utf-8")
                self.send_header("Content-Length", str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b)

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
            self._json({
                "daily_minimums":          DAILY_MINIMUMS,
                "eye_timer_seconds":       EYE_TIMER_SECONDS,
                "warning_advance_seconds": app_vm.config.warning_advance_seconds,
                "idle_threshold_seconds":  IDLE_THRESHOLD,
                "lang":                    app_vm.config.lang,
                "menu_features":           app_vm.config.menu_features,
            })

        def _api_status(self) -> None:
            self._json(app_vm.get_status_dict())

        def _api_exercises(self) -> None:
            record = app_vm.today_record.value
            exs = exercise_svc.pick_exercises(record, app_vm.config)
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
            from core.models.app_config import DAILY_MINIMUMS
            from core.services.scoring import all_minimums_met
            result = records_vm.load_history_list()
            # Always include today with live data
            today = app_vm.today_record.value
            counts = today.category_counts
            result[today_str()] = {
                "total_score":    today.total_score,
                "focus_minutes":  today.focus_minutes,
                "checkins":       len(today.checkins),
                "category_counts": counts,
                "minimums_met":   all_minimums_met(counts),
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
                mood=body.get("mood") or None,
                note=str(body.get("note", "") or ""),
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
            dispatch_fn("playDoneSound:", None)

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
            restroom_subtype = body.get("restroom_subtype") or None

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

            is_restroom = act_id == "restroom"
            away_event  = "restroom" if is_restroom else "away_return"
            away_wc     = (restroom_subtype or wc) if is_restroom else wc
            away_act    = self._lookup_act(act_id)
            away_fs     = focus_score(fm, away_act)
            away_checkin = CheckIn(
                time=now_hhmm(), focus_minutes=fm, score=away_fs,
                work_content=away_wc, activity_type=act_id, event_type=away_event,
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
            prefs_vm.save_plan_settings(body)
            app_vm.sync_timer_from_config()
            self._json({"success": True})
            dispatch_fn("updateMenuAfterPrefs:", None)

        def _api_plan_save(self) -> None:
            from datetime import date as _date, datetime as _dt
            body = self._body()
            text = str(body.get("text", "")).strip()
            if not text:
                self._json({"success": False, "error": "empty"})
                return
            p_prefs = prefs_vm.get_prefs()
            file_path        = p_prefs.get("plan_file_path", "").strip()
            file_pattern     = p_prefs.get("plan_file_pattern", "").strip()
            keyword          = p_prefs.get("plan_file_keyword", "").strip()
            prefix_type      = p_prefs.get("plan_prefix_type", "none")
            prefix_custom    = p_prefs.get("plan_prefix_custom", "")
            not_found_action = p_prefs.get("plan_keyword_not_found", "append")
            if not file_path and not file_pattern:
                self._json({"success": False, "error": "no_path"})
                return
            today_s = _date.today().strftime("%Y-%m-%d")
            now_s   = _dt.now().strftime("%H:%M")
            if prefix_type == "date":
                prefix = today_s + "\n"
            elif prefix_type == "time":
                prefix = now_s + "\n"
            elif prefix_type == "datetime":
                prefix = f"{today_s} {now_s}\n"
            elif prefix_type == "custom" and prefix_custom:
                prefix = prefix_custom.replace("{date}", today_s).replace("{time}", now_s) + "\n"
            else:
                prefix = ""
            insert_text = prefix + text + "\n"
            try:
                # Resolve target file path
                if file_pattern:
                    py_pattern = (file_pattern
                        .replace("YYYY", "%Y").replace("YY", "%y")
                        .replace("MM", "%m").replace("DD", "%d")
                        .replace("HH", "%H").replace("mm", "%M"))
                    filename = _date.today().strftime(py_pattern)
                    base_dir = (Path(file_path).expanduser()
                                if file_path else Path.home() / "Documents")
                    base_dir.mkdir(parents=True, exist_ok=True)
                    p = base_dir / filename
                    if not p.exists():
                        p.write_text("", encoding="utf-8")
                else:
                    p = Path(file_path).expanduser()
                    if not p.exists():
                        self._json({"success": False, "error": "file_not_found"})
                        return
                content = p.read_text(encoding="utf-8")
                if keyword:
                    lines = content.splitlines(keepends=True)
                    insert_idx = None
                    for i, line in enumerate(lines):
                        if keyword in line:
                            insert_idx = i + 1
                            break
                    if insert_idx is not None:
                        lines.insert(insert_idx, insert_text)
                        p.write_text("".join(lines), encoding="utf-8")
                        self._json({"success": True})
                    elif not_found_action == "append":
                        if not content.endswith("\n"):
                            content += "\n"
                        p.write_text(content + "\n" + insert_text, encoding="utf-8")
                        self._json({"success": True})
                    else:
                        self._json({"success": False, "error": "keyword_not_found"})
                else:
                    if not content.endswith("\n"):
                        content += "\n"
                    p.write_text(content + "\n" + insert_text, encoding="utf-8")
                    self._json({"success": True})
            except Exception as e:
                self._json({"success": False, "error": str(e)})

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
                "mood", "note",
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

        def _api_records_add(self) -> None:
            body     = self._body()
            date_str = body.get("date", today_str())
            new_idx  = records_vm.add_checkin(date_str, body)
            if new_idx >= 0 and date_str == today_str():
                app_vm.today_record.value = records_vm.load_today()
            self._json({"success": new_idx >= 0, "index": new_idx})

        def _api_export(self, query_string: str) -> None:
            import csv, io
            from pathlib import Path as _Path
            fmt = "csv" if "csv" in (query_string or "") else "json"
            try:
                # Load full records per date (load_history_list only has count summaries)
                date_keys = sorted(records_vm.load_history_list().keys())
                full_records: dict[str, dict] = {}
                for d in date_keys:
                    rec = records_vm.load_date(d)
                    if rec:
                        full_records[d] = rec.to_dict()
                # Always include today's live data
                full_records[today_str()] = app_vm.today_record.value.to_dict()

                desktop = _Path.home() / "Desktop"
                if not desktop.exists():
                    desktop = _Path.home() / "Downloads"
                ts = datetime.now().strftime("%Y%m%d-%H%M%S")

                if fmt == "json":
                    dest = desktop / f"reset-backup-{ts}.json"
                    dest.write_text(
                        json.dumps(full_records, ensure_ascii=False, indent=2),
                        encoding="utf-8")
                else:
                    dest = desktop / f"reset-backup-{ts}.csv"
                    out = io.StringIO()
                    w = csv.writer(out)
                    w.writerow(["date", "time", "focus_minutes", "score",
                                "activity_type", "work_content", "event_type"])
                    for date_s, rec in sorted(full_records.items()):
                        for c in rec.get("checkins", []):
                            w.writerow([
                                date_s,
                                c.get("time", ""),
                                c.get("focus_minutes", ""),
                                c.get("score", ""),
                                c.get("activity_type", ""),
                                c.get("work_content", ""),
                                c.get("event_type", "break"),
                            ])
                    dest.write_text(out.getvalue(), encoding="utf-8")

                self._json({"success": True, "path": str(dest)})
            except Exception as e:
                self._json({"error": str(e)}, 500)

        def _api_muscle_stats(self) -> None:
            """Aggregate muscle_groups counts; supports ?range=7 or ?range=30."""
            from datetime import datetime, timedelta
            from urllib.parse import parse_qs, urlparse
            qs = parse_qs(urlparse(self.path).query)
            range_days = qs.get("range", [None])[0]
            cutoff: str | None = None
            if range_days:
                cutoff = (datetime.now() - timedelta(days=int(range_days))).strftime("%Y-%m-%d")
            counts: dict = {}
            for date_str in records_vm.load_history_list():
                if cutoff and date_str < cutoff:
                    continue
                rec = records_vm.load_date(date_str)
                if rec:
                    for c in rec.checkins:
                        if c.exercise and isinstance(c.exercise, dict):
                            for mg in c.exercise.get("muscle_groups", []):
                                counts[mg] = counts.get(mg, 0) + 1
            today = datetime.now().strftime("%Y-%m-%d")
            if not cutoff or today >= cutoff:
                for c in app_vm.today_record.value.checkins:
                    if c.exercise and isinstance(c.exercise, dict):
                        for mg in c.exercise.get("muscle_groups", []):
                            counts[mg] = counts.get(mg, 0) + 1
            self._json(counts)

        def _api_exercise_stats(self) -> None:
            """Count how many times each exercise id has appeared in check-ins."""
            counts: dict = {}
            for date_str in records_vm.load_history_list():
                rec = records_vm.load_date(date_str)
                if rec:
                    for c in rec.checkins:
                        if c.exercise and isinstance(c.exercise, dict):
                            ex_id = c.exercise.get("id")
                            if ex_id:
                                counts[ex_id] = counts.get(ex_id, 0) + 1
            for c in app_vm.today_record.value.checkins:
                if c.exercise and isinstance(c.exercise, dict):
                    ex_id = c.exercise.get("id")
                    if ex_id:
                        counts[ex_id] = counts.get(ex_id, 0) + 1
            self._json(counts)

        def _api_restroom_stats(self) -> None:
            """Aggregate restroom visit data across all history."""
            from datetime import datetime, timedelta

            def is_restroom(c) -> bool:
                return c.event_type in ("restroom",) or c.activity_type == "restroom"

            def subtype(c) -> str:
                wc = (c.work_content or "").strip().lower()
                if wc in ("big", "small"):
                    return wc
                return "unknown"

            today = datetime.now().strftime("%Y-%m-%d")
            week_cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

            result = {"today": {"total": 0, "small": 0, "big": 0, "times": []},
                      "week":  {"total": 0, "small": 0, "big": 0},
                      "all":   {"total": 0, "small": 0, "big": 0},
                      "avg_interval_min": None}
            all_times: list[str] = []

            hist = sorted(records_vm.load_history_list().keys())
            all_dates = [d for d in hist if d != today] + [today]
            for date_str in all_dates:
                if date_str == today:
                    checkins = app_vm.today_record.value.checkins
                else:
                    rec = records_vm.load_date(date_str)
                    checkins = rec.checkins if rec else []
                for c in checkins:
                    if not is_restroom(c):
                        continue
                    st = subtype(c)
                    result["all"]["total"] += 1
                    if st == "small": result["all"]["small"] += 1
                    if st == "big":   result["all"]["big"] += 1
                    if date_str >= week_cutoff:
                        result["week"]["total"] += 1
                        if st == "small": result["week"]["small"] += 1
                        if st == "big":   result["week"]["big"] += 1
                    if date_str == today:
                        result["today"]["total"] += 1
                        if st == "small": result["today"]["small"] += 1
                        if st == "big":   result["today"]["big"] += 1
                        if c.time:
                            result["today"]["times"].append(c.time)
                            all_times.append(f"{date_str} {c.time}")

            if len(all_times) >= 2:
                all_times.sort()
                intervals = []
                for i in range(1, len(all_times)):
                    def _min(t):
                        parts = t.split()
                        h, m = map(int, parts[1].split(":"))
                        return h * 60 + m
                    intervals.append(_min(all_times[i]) - _min(all_times[i - 1]))
                pos = [x for x in intervals if x > 0]
                if pos:
                    result["avg_interval_min"] = round(sum(pos) / len(pos))
            self._json(result)

        def _api_alerts_get(self) -> None:
            self._json(app_vm.config.scheduled_alerts)

        def _api_alerts_post(self) -> None:
            body = self._body()
            if not isinstance(body, list):
                self._json({"error": "expected list"}, 400)
                return
            alerts = []
            for item in body:
                if not isinstance(item, dict):
                    continue
                atype = str(item.get("type", "daily"))
                if atype == "daily" and not item.get("time"):
                    continue
                if atype == "once" and not item.get("fire_at"):
                    continue
                entry: dict = {
                    "id":      str(item.get("id", "")),
                    "type":    atype,
                    "message": str(item.get("message", "")),
                    "enabled": bool(item.get("enabled", True)),
                }
                if atype == "daily":
                    entry["time"] = str(item.get("time", ""))
                else:
                    entry["fire_at"] = str(item.get("fire_at", ""))
                alerts.append(entry)
            persistence.update_config(scheduled_alerts=alerts)
            app_vm.config.scheduled_alerts = alerts
            self._json({"success": True})

        def _serve_custom_alert(self, _query: str) -> None:
            self._serve_file("custom_alert.html")

        def _api_exercises_library_get(self) -> None:
            """Return all exercises (built-in + user-contributed) for the library editor."""
            all_exs = exercise_svc.load()
            self._json([e.to_dict() for e in all_exs])

        def _api_exercises_library_post(self) -> None:
            """Save user-contributed exercises to the user exercises file."""
            body = self._body()
            if not isinstance(body, list):
                self.send_response(400)
                self.end_headers()
                return
            try:
                from core.models.exercise import Exercise
                cleaned = [Exercise.from_dict(d).to_dict() for d in body if isinstance(d, dict) and d.get("id")]
                if exercise_svc._user_file is None:
                    self._json({"success": False, "error": "no_user_file"}, 400)
                    return
                exercise_svc._user_file.parent.mkdir(parents=True, exist_ok=True)
                exercise_svc._user_file.write_text(
                    json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                exercise_svc.invalidate_cache()
                self._json({"success": True, "count": len(cleaned)})
            except Exception as e:
                self._json({"success": False, "error": str(e)}, 500)

        def _serve_exercise_img(self, path: str) -> None:
            """Serve images from ui/exercises/img/."""
            import mimetypes
            rel = path.lstrip("/")  # e.g. "exercises/img/T01.png"
            img_path = resource_dir / rel
            if not img_path.exists():
                self.send_response(404)
                self.end_headers()
                return
            mime = mimetypes.guess_type(str(img_path))[0] or "application/octet-stream"
            b = img_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(b)))
            self.send_header("Cache-Control", "max-age=3600")
            self.end_headers()
            self.wfile.write(b)

        def _api_reset_data(self) -> None:
            from core.models.daily_record import DailyRecord
            try:
                empty = DailyRecord(date=today_str())
                app_vm._persistence.save_state(empty)  # type: ignore[attr-defined]
                app_vm.today_record.value = empty
                self._json({"success": True})
            except Exception as e:
                self._json({"success": False, "error": str(e)}, 500)

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
