"""Tool: qa_generate_evidence — gera script Appium runtime + evidências."""

from __future__ import annotations

import json
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP

from guardiao_mcp.contract import fail
from lib.mobile.qa_generate_evidence import _summary_ok, run_qa_generate_evidence

DESCRIPTION = """\
**Quando:** após `qa_pipeline_evidence` com `apps_ready_ok=true` e `binding.ok=true`.

**Entrada:** `pipeline_result` — JSON completo de `qa_pipeline_evidence` (`scenario_pipeline` + `device`).

**Faz:** seed → gera script Appium runtime a partir de `steps`/`device` (seed embutido) → executa → evidências.
Default `dry_run=false` (evidência real). Steps `optional` com settle/retry; pós-`force_reload` re-pareia
se voltar ao PrePairing; assert de saudação via text + contentDescription; hooks genéricos
(`dismiss_expo`, `grant_os_perms`, `force_reload`); stabilize + permissões SO.

**Retorno (`result`):**
```
{
  "ticket_id": "",
  "scenario_id": "",
  "screenshot": {"evidence": "caminho", "error_runtime": {"type": "", "description": ""}},
  "video_record": {"evidence": "caminho", "error_runtime": {"type": "", "description": ""}}
}
```
"""


def qa_generate_evidence(
    pipeline_result: Annotated[
        str,
        "JSON completo retornado por qa_pipeline_evidence (envelope ou result)",
    ],
    dry_run: Annotated[bool, "false executa Appium e gera evidência; true só gera script"] = False,
    timeout_sec: Annotated[int, "Timeout suite (s)"] = 900,
) -> str:
    """Gera script Appium em runtime a partir do pipeline e produz evidências."""
    try:
        summary: dict[str, Any] = run_qa_generate_evidence(
            pipeline_result=pipeline_result,
            dry_run=dry_run,
            timeout_sec=timeout_sec,
        )
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}", dry_run=dry_run)

    passed = _summary_ok(summary)
    shot_err = (summary.get("screenshot") or {}).get("error_runtime") or {}
    vid_err = (summary.get("video_record") or {}).get("error_runtime") or {}
    err = shot_err.get("type") or vid_err.get("type") or None
    return json.dumps(
        {
            "ok": passed,
            "dry_run": dry_run,
            "result": summary,
            "error": None if passed else err,
        },
        ensure_ascii=False,
        indent=2,
        default=str,
    )


def register(mcp: FastMCP) -> None:
    mcp.tool(description=DESCRIPTION)(qa_generate_evidence)
