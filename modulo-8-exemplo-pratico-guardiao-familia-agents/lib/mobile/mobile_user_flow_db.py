"""SQLite local — fluxos de usuário mobile (telas, labels, passos 0→N)."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from lib.paths import MODULE_ROOT

DEFAULT_DB = MODULE_ROOT / "data" / "mobile_user_flows.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS mobile_apps (
  app_id TEXT PRIMARY KEY,
  repo TEXT NOT NULL,
  bundle_id TEXT,
  metro_port INTEGER,
  emulator TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS mobile_screens (
  screen_id TEXT PRIMARY KEY,
  app_id TEXT NOT NULL,
  component_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  route_condition TEXT,
  FOREIGN KEY (app_id) REFERENCES mobile_apps(app_id)
);

CREATE TABLE IF NOT EXISTS mobile_elements (
  element_id TEXT PRIMARY KEY,
  screen_id TEXT NOT NULL,
  element_kind TEXT NOT NULL,
  label_text TEXT,
  test_id TEXT,
  accessibility_label TEXT,
  style_key TEXT,
  file_path TEXT,
  line_hint INTEGER,
  discovery_source TEXT DEFAULT 'static',
  FOREIGN KEY (screen_id) REFERENCES mobile_screens(screen_id)
);

CREATE TABLE IF NOT EXISTS mobile_user_flows (
  flow_id TEXT PRIMARY KEY,
  app_id TEXT NOT NULL,
  entry_point TEXT NOT NULL,
  target_element_id TEXT,
  target_screen_id TEXT NOT NULL,
  flow_name TEXT NOT NULL,
  preconditions_json TEXT,
  qa_repro_steps_json TEXT,
  mermaid TEXT,
  discovery_source TEXT DEFAULT 'static',
  discovered_at TEXT,
  FOREIGN KEY (app_id) REFERENCES mobile_apps(app_id)
);

CREATE TABLE IF NOT EXISTS mobile_flow_steps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  flow_id TEXT NOT NULL,
  step_order INTEGER NOT NULL,
  screen_id TEXT,
  user_action TEXT NOT NULL,
  system_behavior TEXT NOT NULL,
  navigation_file TEXT,
  route_condition TEXT,
  FOREIGN KEY (flow_id) REFERENCES mobile_user_flows(flow_id)
);

CREATE TABLE IF NOT EXISTS mobile_discovery_runs (
  run_id TEXT PRIMARY KEY,
  app_id TEXT,
  started_at TEXT,
  finished_at TEXT,
  status TEXT,
  elements_found INTEGER DEFAULT 0,
  flows_seeded INTEGER DEFAULT 0,
  notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_elements_label ON mobile_elements(label_text);
CREATE INDEX IF NOT EXISTS idx_elements_screen ON mobile_elements(screen_id);
CREATE INDEX IF NOT EXISTS idx_flows_target ON mobile_user_flows(target_element_id);
CREATE INDEX IF NOT EXISTS idx_flows_screen ON mobile_user_flows(target_screen_id);
CREATE INDEX IF NOT EXISTS idx_steps_flow ON mobile_flow_steps(flow_id, step_order);
"""


def db_path() -> Path:
    raw = (os.environ.get("GUARDAO_MOBILE_FLOW_DB") or "").strip()
    return Path(raw) if raw else DEFAULT_DB


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connect(db: Path | None = None) -> Iterator[sqlite3.Connection]:
    path = db or db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def upsert_app(
    app_id: str,
    *,
    repo: str,
    bundle_id: str = "",
    metro_port: int = 0,
    emulator: str = "",
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO mobile_apps (app_id, repo, bundle_id, metro_port, emulator, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(app_id) DO UPDATE SET
              repo=excluded.repo, bundle_id=excluded.bundle_id,
              metro_port=excluded.metro_port, emulator=excluded.emulator,
              updated_at=excluded.updated_at
            """,
            (app_id, repo, bundle_id, metro_port, emulator, _now()),
        )


def upsert_screen(
    screen_id: str,
    *,
    app_id: str,
    component_name: str,
    file_path: str,
    route_condition: str = "",
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO mobile_screens (screen_id, app_id, component_name, file_path, route_condition)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(screen_id) DO UPDATE SET
              file_path=excluded.file_path, route_condition=excluded.route_condition
            """,
            (screen_id, app_id, component_name, file_path, route_condition),
        )


def upsert_element(
    element_id: str,
    *,
    screen_id: str,
    element_kind: str,
    label_text: str = "",
    test_id: str = "",
    accessibility_label: str = "",
    style_key: str = "",
    file_path: str = "",
    line_hint: int = 0,
    discovery_source: str = "static",
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO mobile_elements (
              element_id, screen_id, element_kind, label_text, test_id,
              accessibility_label, style_key, file_path, line_hint, discovery_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(element_id) DO UPDATE SET
              label_text=excluded.label_text, test_id=excluded.test_id,
              accessibility_label=excluded.accessibility_label,
              style_key=excluded.style_key, file_path=excluded.file_path,
              line_hint=excluded.line_hint, discovery_source=excluded.discovery_source
            """,
            (
                element_id,
                screen_id,
                element_kind,
                label_text,
                test_id,
                accessibility_label,
                style_key,
                file_path,
                line_hint,
                discovery_source,
            ),
        )


def upsert_flow(
    flow_id: str,
    *,
    app_id: str,
    entry_point: str,
    target_screen_id: str,
    flow_name: str,
    target_element_id: str = "",
    preconditions: list[str] | None = None,
    qa_repro_steps: list[str] | None = None,
    mermaid: str = "",
    discovery_source: str = "static",
    steps: list[dict[str, Any]] | None = None,
) -> None:
    pre_json = json.dumps(preconditions or [], ensure_ascii=False)
    qa_json = json.dumps(qa_repro_steps or [], ensure_ascii=False)
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO mobile_user_flows (
              flow_id, app_id, entry_point, target_element_id, target_screen_id,
              flow_name, preconditions_json, qa_repro_steps_json, mermaid,
              discovery_source, discovered_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(flow_id) DO UPDATE SET
              entry_point=excluded.entry_point,
              target_element_id=excluded.target_element_id,
              flow_name=excluded.flow_name,
              preconditions_json=excluded.preconditions_json,
              qa_repro_steps_json=excluded.qa_repro_steps_json,
              mermaid=excluded.mermaid,
              discovery_source=excluded.discovery_source,
              discovered_at=excluded.discovered_at
            """,
            (
                flow_id,
                app_id,
                entry_point,
                target_element_id,
                target_screen_id,
                flow_name,
                pre_json,
                qa_json,
                mermaid,
                discovery_source,
                _now(),
            ),
        )
        conn.execute("DELETE FROM mobile_flow_steps WHERE flow_id = ?", (flow_id,))
        for s in steps or []:
            conn.execute(
                """
                INSERT INTO mobile_flow_steps (
                  flow_id, step_order, screen_id, user_action, system_behavior,
                  navigation_file, route_condition
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    flow_id,
                    int(s.get("order", 0)),
                    s.get("screen_id") or s.get("screen", ""),
                    s.get("user_action", ""),
                    s.get("system_behavior", ""),
                    s.get("navigation_file") or s.get("file", ""),
                    s.get("route_condition", ""),
                ),
            )


def start_discovery_run(app_id: str, notes: str = "") -> str:
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO mobile_discovery_runs (run_id, app_id, started_at, status, notes)
            VALUES (?, ?, ?, 'running', ?)
            """,
            (run_id, app_id, _now(), notes),
        )
    return run_id


def finish_discovery_run(
    run_id: str,
    *,
    status: str,
    elements_found: int,
    flows_seeded: int,
    notes: str = "",
) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE mobile_discovery_runs SET
              finished_at=?, status=?, elements_found=?, flows_seeded=?, notes=?
            WHERE run_id=?
            """,
            (_now(), status, elements_found, flows_seeded, notes, run_id),
        )


def get_flow(flow_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM mobile_user_flows WHERE flow_id = ?", (flow_id,)
        ).fetchone()
        if not row:
            return None
        return _hydrate_flow(conn, dict(row))


def find_flows_for_task(
    *,
    app_id: str = "",
    screen_hint: str = "",
    file_hint: str = "",
    label_hint: str = "",
    element_id: str = "",
) -> list[dict[str, Any]]:
    """Busca fluxos por element_id, tela, arquivo ou texto de label."""
    with connect() as conn:
        if element_id:
            rows = conn.execute(
                "SELECT * FROM mobile_user_flows WHERE target_element_id = ?",
                (element_id,),
            ).fetchall()
            if rows:
                return [_hydrate_flow(conn, dict(r)) for r in rows]

        clauses: list[str] = []
        params: list[Any] = []
        if app_id:
            clauses.append("f.app_id = ?")
            params.append(app_id)
        if screen_hint:
            clauses.append("(f.target_screen_id LIKE ? OR s.component_name LIKE ?)")
            params.extend([f"%{screen_hint}%", f"%{screen_hint}%"])
        if file_hint:
            clauses.append("(s.file_path LIKE ? OR e.file_path LIKE ?)")
            params.extend([f"%{file_hint}%", f"%{file_hint}%"])
        if label_hint:
            clauses.append("(e.label_text LIKE ? OR e.accessibility_label LIKE ? OR f.flow_name LIKE ?)")
            params.extend([f"%{label_hint}%", f"%{label_hint}%", f"%{label_hint}%"])

        if not clauses:
            return []

        sql = f"""
            SELECT DISTINCT f.* FROM mobile_user_flows f
            LEFT JOIN mobile_screens s ON s.screen_id = f.target_screen_id
            LEFT JOIN mobile_elements e ON e.element_id = f.target_element_id
            WHERE {' AND '.join(clauses)}
            ORDER BY f.discovered_at DESC
            LIMIT 5
        """
        rows = conn.execute(sql, params).fetchall()
        return [_hydrate_flow(conn, dict(r)) for r in rows]


def _hydrate_flow(conn: sqlite3.Connection, flow: dict[str, Any]) -> dict[str, Any]:
    steps = conn.execute(
        """
        SELECT step_order, screen_id, user_action, system_behavior,
               navigation_file, route_condition
        FROM mobile_flow_steps WHERE flow_id = ? ORDER BY step_order
        """,
        (flow["flow_id"],),
    ).fetchall()
    flow["preconditions"] = json.loads(flow.pop("preconditions_json") or "[]")
    flow["qa_repro_steps"] = json.loads(flow.pop("qa_repro_steps_json") or "[]")
    flow["steps"] = [
        {
            "order": r["step_order"],
            "screen_id": r["screen_id"],
            "screen": r["screen_id"].split(":", 1)[-1] if r["screen_id"] else "",
            "user_action": r["user_action"],
            "system_behavior": r["system_behavior"],
            "file": r["navigation_file"],
            "route_condition": r["route_condition"],
        }
        for r in steps
    ]
    if flow.get("target_element_id"):
        el = conn.execute(
            "SELECT * FROM mobile_elements WHERE element_id = ?",
            (flow["target_element_id"],),
        ).fetchone()
        flow["target_element"] = dict(el) if el else None
    return flow


def flow_to_refinement_user_flow(flow: dict[str, Any], app_row: dict[str, Any] | None = None) -> dict[str, Any]:
    """Converte registro DB → refinement.user_flow para tickets."""
    app_id = flow["app_id"]
    app_row = app_row or {}
    screen_name = flow["target_screen_id"].split(":", 1)[-1] if flow.get("target_screen_id") else ""
    target_el = flow.get("target_element") or {}
    label = target_el.get("label_text") or target_el.get("accessibility_label") or flow.get("flow_name", "")
    style = target_el.get("style_key") or ""
    target_element = f"{target_el.get('element_kind', 'Text')} {style or label}".strip()

    return {
        "app": app_row.get("repo") or app_id,
        "entry_point": flow.get("entry_point", "cold start"),
        "preconditions": flow.get("preconditions") or [],
        "navigation_files": list(
            dict.fromkeys(
                s.get("file") for s in flow.get("steps", []) if s.get("file")
            )
        ),
        "target_screen": screen_name,
        "target_element": target_element,
        "emulator": app_row.get("emulator", ""),
        "metro_port": app_row.get("metro_port", 0),
        "steps": [
            {
                "order": s["order"],
                "screen": s.get("screen") or s.get("screen_id", ""),
                "user_action": s["user_action"],
                "system_behavior": s["system_behavior"],
                "file": s.get("file", ""),
                "route_condition": s.get("route_condition", ""),
            }
            for s in flow.get("steps", [])
        ],
        "mermaid": flow.get("mermaid") or "",
        "qa_repro_steps": flow.get("qa_repro_steps") or [],
        "flow_id": flow.get("flow_id"),
        "discovery_source": flow.get("discovery_source"),
    }


def stats() -> dict[str, int]:
    with connect() as conn:
        return {
            "apps": conn.execute("SELECT COUNT(*) FROM mobile_apps").fetchone()[0],
            "screens": conn.execute("SELECT COUNT(*) FROM mobile_screens").fetchone()[0],
            "elements": conn.execute("SELECT COUNT(*) FROM mobile_elements").fetchone()[0],
            "flows": conn.execute("SELECT COUNT(*) FROM mobile_user_flows").fetchone()[0],
        }
