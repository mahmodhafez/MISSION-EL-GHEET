"""SQLite access: one connection per call, WAL, foreign keys on. Transcripts are never stored."""
from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


class Store:
    def __init__(self, path: Path):
        self.path = path
        if str(path) != ":memory:":
            path.parent.mkdir(parents=True, exist_ok=True)
        with self.tx() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def tx(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # daily ceilings (public deployment, backend design §10a)
    def take_daily(self, kind: str, ceiling: int) -> bool:
        """Count one use of `kind` today (UTC); False once today's ceiling is reached."""
        day = now()[:10]
        with self.tx() as c:
            c.execute("INSERT INTO usage VALUES (?,?,0) ON CONFLICT(day, kind) DO NOTHING", (day, kind))
            row = c.execute("UPDATE usage SET count = count + 1 WHERE day=? AND kind=? AND count < ? RETURNING count",
                            (day, kind, ceiling)).fetchone()
        return row is not None

    # scenarios
    def create_scenario(self, data_release: str, payload: dict) -> dict:
        sid, t = new_id("scn"), now()
        with self.tx() as c:
            c.execute("INSERT INTO scenarios VALUES (?,?,?,?,?,?)", (sid, 1, data_release, json.dumps(payload), t, t))
        return self.get_scenario(sid)

    def get_scenario(self, sid: str) -> dict | None:
        with self.tx() as c:
            r = c.execute("SELECT * FROM scenarios WHERE id=?", (sid,)).fetchone()
        return None if r is None else {"id": r["id"], "revision": r["revision"], "data_release": r["data_release"],
                                       "input": json.loads(r["input_json"]), "created_at": r["created_at"], "updated_at": r["updated_at"]}

    def revise_scenario(self, sid: str, expected_revision: int, payload: dict) -> dict | None:
        """Full replacement only if the caller saw the current revision (expected_revision). None = conflict."""
        with self.tx() as c:
            cur = c.execute("UPDATE scenarios SET revision=revision+1, input_json=?, updated_at=? WHERE id=? AND revision=?",
                            (json.dumps(payload), now(), sid, expected_revision))
            if cur.rowcount == 0:
                return None
        return self.get_scenario(sid)

    # results
    def add_result(self, sid: str, revision: int, kind: str, data_release: str, payload: dict) -> str:
        rid = new_id("res")
        with self.tx() as c:
            c.execute("INSERT INTO results VALUES (?,?,?,?,?,?,?)", (rid, sid, revision, kind, data_release, json.dumps(payload), now()))
        return rid

    def get_result(self, rid: str) -> dict | None:
        with self.tx() as c:
            r = c.execute("SELECT * FROM results WHERE id=?", (rid,)).fetchone()
        return None if r is None else {"id": r["id"], "scenario_id": r["scenario_id"], "revision": r["revision"], "kind": r["kind"],
                                       "data_release": r["data_release"], "payload": json.loads(r["payload_json"]), "created_at": r["created_at"]}

    # evidence cards
    def add_card(self, sid: str, revision: int, result_id: str, payload: dict) -> str:
        cid = new_id("card")
        with self.tx() as c:
            c.execute("INSERT INTO evidence_cards VALUES (?,?,?,?,?,?)", (cid, sid, revision, result_id, json.dumps(payload), now()))
        return cid

    def get_card(self, cid: str) -> dict | None:
        with self.tx() as c:
            r = c.execute("SELECT * FROM evidence_cards WHERE id=?", (cid,)).fetchone()
        return None if r is None else {"id": r["id"], "scenario_id": r["scenario_id"], "revision": r["revision"],
                                       "result_id": r["result_id"], "payload": json.loads(r["payload_json"]), "created_at": r["created_at"]}
