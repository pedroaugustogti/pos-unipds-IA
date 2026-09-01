#!/usr/bin/env python3
"""Atualiza issue #103 (T-P3-009) com instruções MCP qa-gate."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = "guardiaofamilia/guardiao-familia-child"
ISSUE = 103

QA_GATE_01 = r"""### `qa-gate`

- **Preferir MCP** servidor `guardiao-familia-agents` (`list_mcp_tools`) — fallback: `agents/qa-gate/scripts/`
- `get_handoff` + `append_task_action_tool` + `emit_status_event` `start_test` (`dry_run=false`)
- `query_mobile_flow_rag(query="T-P3-009 ChildHomeV2 greeting header", task_id="T-P3-009")` — plano de telas/evidência
- **Seed:** `qa_db_seed(task_id="T-P3-009", profile="child_home", use_task_config=true, dry_run=false)` — Postgres + `stage-handoff.json` (retoma após `paste_code_parent`)
- **Suite Appium:** `qa_appium_suite_child(from_db_seed=true, task_id="T-P3-009", feature="pairing", phase="Smoke", dry_run=false)` — dual emulator (5554+5556), Metro child 9090, pairing→ChildHome
- Validar header `ChildHomeV2` nos 3 horários (emulador **5556**): 08:00 → **Bom dia** · 15:00 → **Boa tarde** · 21:00 → **Boa noite**
- Evidências: 3 PNG + 3 MP4 + JSON em `agents/00-runtime/output/mobile/qa_evidence/T-P3-009/`
- **Cleanup:** `qa_db_cleanup(task_id="T-P3-009", dry_run=false)` quando `qa.db_seed.cleanup=true`
- `emit_status_event` `test_passed` ou `test_failed_bug` + comentário sec. 10.3 — **não** alterar código da feature

#### Sequência MCP (ordem obrigatória)

```
1. list_mcp_tools()
2. get_handoff(task_id="T-P3-009")
3. emit_status_event(task_id="T-P3-009", event="start_test", dry_run=false)
4. query_mobile_flow_rag(query="child home greeting ChildHomeV2", task_id="T-P3-009")
5. qa_db_seed(task_id="T-P3-009", profile="child_home", use_task_config=true, dry_run=false)
6. qa_appium_suite_child(from_db_seed=true, task_id="T-P3-009", feature="pairing", phase="Smoke", dry_run=false)
   # Após suite: adb date 08:00 / 15:00 / 21:00 + screenshot header (3 PNG) + MP4 por período
7. qa_db_cleanup(task_id="T-P3-009", dry_run=false)
8. emit_status_event(task_id="T-P3-009", event="test_passed"|"test_failed_bug", dry_run=false)
```

#### Fallback CLI (MCP indisponível)

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/qa-gate/scripts/mobile_e2e_seed.py --task T-P3-009 --profile child_home
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle --record-video
python agents/qa-gate/scripts/mobile_e2e_seed.py --task T-P3-009 --cleanup-only
```
"""

SEC6 = r"""## 6. QA (qa-gate)

| Campo | Valor |
|-------|-------|
| test_suite | `qa-mobile-child-appium` |
| Cenários | greeting-morning-08h, greeting-afternoon-15h, greeting-evening-21h, pairing-to-child-home-e2e |
| Evidências obrigatórias | screenshot png, video mp4, json report, scenarios count, video scope |
| MCP server | `guardiao-familia-agents` (`list_mcp_tools`) |
| Skill | `modulo-8-.../agents/qa-gate/SKILL.md` · `MOBILE_SETUP_EVIDENCE.md` |

### DB seed + suite (MCP — preferido)

| Passo | Tool MCP | Parâmetros |
|-------|----------|------------|
| 1 | `get_handoff` | `task_id=T-P3-009` |
| 2 | `emit_status_event` | `event=start_test`, `dry_run=false` |
| 3 | `query_mobile_flow_rag` | `query=ChildHomeV2 greeting`, `task_id=T-P3-009` |
| 4 | `qa_db_seed` | `task_id=T-P3-009`, `profile=child_home`, `use_task_config=true`, `dry_run=false` |
| 5 | `qa_appium_suite_child` | `from_db_seed=true`, `task_id=T-P3-009`, `feature=pairing`, `phase=Smoke`, `dry_run=false` |
| 6 | (manual adb) | `adb -s emulator-5556 shell date` 08:00 / 15:00 / 21:00 + screenshots header |
| 7 | `qa_db_cleanup` | `task_id=T-P3-009`, `dry_run=false` |
| 8 | `emit_status_event` | `test_passed` ou `test_failed_bug`, `dry_run=false` |

### DB seed (config ticket)

| Campo | Valor |
|-------|-------|
| enabled | `True` |
| profile | `child_home` — API: família+filho+código; Appium retoma após `paste_code_parent` → home child |
| family_name | `QA Evidence T-P3-009` |
| child_name | `Filho QA T-P3-009` |
| resume_after_step | `paste_code_parent` |
| cleanup | `True` pós-evidência |

**Dependências:** Docker (Postgres/Redis/API) · `guardiao-familia-mobile-setup` · emuladores 5554/5556 · MCP `guardiao-familia-agents` habilitado no Cursor

**Fallback CLI:**

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/qa-gate/scripts/mobile_e2e_seed.py --task T-P3-009 --profile child_home
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle --record-video
python agents/qa-gate/scripts/mobile_e2e_seed.py --task T-P3-009 --cleanup-only
```

**Regra:** se qualquer AC = FAIL → `test_failed_bug` + comentário qa-gate (sec. 10). Não merge.

"""


def fetch_body() -> str:
    out = subprocess.check_output(
        ["gh", "api", f"repos/{REPO}/issues/{ISSUE}", "--jq", ".body"],
        encoding="utf-8",
    )
    return json.loads(out) if out.startswith('"') else out


QA_GATE_JSON = '''"qa-gate": [
      "MCP: qa_db_seed(T-P3-009, child_home, dry_run=false) + qa_appium_suite_child(from_db_seed=true, feature=pairing, dry_run=false)",
      "MCP: query_mobile_flow_rag + get_handoff + append_task_action_tool + emit_status_event (start_test / test_passed / test_failed_bug)",
      "Validar greeting 08:00/15:00/21:00 no emulador-5556 (Bom dia / Boa tarde / Boa noite)",
      "Evidências em agents/00-runtime/output/mobile/qa_evidence/T-P3-009/ (3 PNG + 3 MP4 + JSON)",
      "MCP: qa_db_cleanup(T-P3-009, dry_run=false) se cleanup=true",
      "Fallback CLI: agents/qa-gate/scripts/mobile_e2e_seed.py + qa_mobile_evidence.py"
    ]'''


def patch(body: str) -> str:
    # Idempotente: substitui bloco qa-gate inteiro até próximo ### `agent`
    body = re.sub(
        r"### `qa-gate`.*?(?=\n### `|\n## )",
        QA_GATE_01.rstrip() + "\n\n",
        body,
        count=1,
        flags=re.DOTALL,
    )
    # Remove duplicatas de Sequência MCP / Fallback CLI
    while body.count("#### Sequência MCP (ordem obrigatória)") > 1:
        body = re.sub(
            r"\n+#### Sequência MCP \(ordem obrigatória\).*?```\n",
            "\n",
            body,
            count=1,
            flags=re.DOTALL,
        )
    body = body.replace(
        "| QA | In Test | **qa-gate** | `skills/qa-gate/SKILL.md` ou `skills/qa/` | Merge PR |",
        "| QA | In Test | **qa-gate** | `agents/qa-gate/SKILL.md` + MCP `guardiao-familia-agents` | Merge PR |",
    )
    old_repro = (
        "### Reproduzir (QA / Appium)\n"
        "1. Subir stack: `python scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle`\n"
        "2. Ajustar hora do emulador para 08:00 → screenshot header (Bom dia)\n"
        "3. Ajustar hora para 15:00 → screenshot header (Boa tarde)\n"
        "4. Ajustar hora para 21:00 → screenshot header (Boa noite)\n"
        "5. Gravar MP4 de cada cenário desde PrePairing até home (ou pairing completo + jump de relógio)"
    )
    new_repro = (
        "### Reproduzir (QA / Appium) — **MCP preferido**\n\n"
        "1. `qa_db_seed(task_id=\"T-P3-009\", profile=\"child_home\", dry_run=false)`\n"
        "2. `qa_appium_suite_child(from_db_seed=true, task_id=\"T-P3-009\", feature=\"pairing\", dry_run=false)`\n"
        "3. Ajustar hora emulador-5556: 08:00 → screenshot header (**Bom dia**)\n"
        "4. 15:00 → screenshot (**Boa tarde**) · 21:00 → screenshot (**Boa noite**)\n"
        "5. MP4 por período (pairing→home ou jump de relógio na home)\n"
        "6. `qa_db_cleanup(task_id=\"T-P3-009\", dry_run=false)`\n\n"
        "Fallback: `python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle --record-video`"
    )
    body = body.replace(old_repro, new_repro)
    body = body.replace(
        "| AC-03 | `python scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle --record-video` | 3 PNG + 3 MP4 em crew/output/mobile_evidence/T-P3-009/ |",
        "| AC-03 | MCP: `qa_db_seed` + `qa_appium_suite_child(from_db_seed=true)` + 3 horários adb | 3 PNG + 3 MP4 em `agents/00-runtime/output/mobile/qa_evidence/T-P3-009/` |",
    )
    body = re.sub(
        r"## 6\. QA \(qa-gate\).*?(?=\n## 7\. Parar)",
        SEC6,
        body,
        flags=re.DOTALL,
    )
    body = re.sub(
        r'"qa-gate": \[[^\]]*\]',
        QA_GATE_JSON,
        body,
        count=1,
        flags=re.DOTALL,
    )
    body = body.replace(
        '"command": "python scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle --record-video",\n        "expected": "3 PNG + 3 MP4 em crew/output/mobile_evidence/T-P3-009/"',
        '"command": "MCP qa_db_seed + qa_appium_suite_child(from_db_seed=true) + adb horários 08/15/21h",\n        "expected": "3 PNG + 3 MP4 em agents/00-runtime/output/mobile/qa_evidence/T-P3-009/"',
    )
    body = body.replace(
        '"how_to_run": "cd modulo-8-exemplo-pratico-guardiao-familia-agents && python scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle --record-video"',
        '"how_to_run": "MCP: qa_db_seed + qa_appium_suite_child(from_db_seed=true); fallback: agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle --record-video"',
    )
    body = body.replace(
        "### Comandos executados\n```\n\n```",
        "### Comandos executados (MCP)\n```\nqa_db_seed / qa_appium_suite_child / qa_db_cleanup / emit_status_event\n```",
        1,
    )
    body = body.replace(
        "[`MOBILE_USER_FLOW_TEMPLATE.md`](docs/templates/MOBILE_USER_FLOW_TEMPLATE.md)",
        "[`MOBILE_USER_FLOW_TEMPLATE.md`](https://github.com/guardiaofamilia/pos-unipds-IA/blob/main/modulo-8-exemplo-pratico-guardiao-familia-agents/board_automation/templates/MOBILE_USER_FLOW_TEMPLATE.md)",
    )
    body = body.replace(
        "Subir stack: `python scripts/qa_mobile_evidence.py --task T-P3-009 --feature pairing --mode cycle`",
        "MCP: qa_db_seed + qa_appium_suite_child(from_db_seed=true, task_id=T-P3-009, feature=pairing)",
    )
    return body


def main() -> int:
    dry = "--dry-run" in sys.argv
    src = Path(__file__).resolve().parents[5] / ".issue-103-body.md"
    if src.is_file() and "--from-cache" in sys.argv:
        body = patch(src.read_text(encoding="utf-8"))
    else:
        body = patch(fetch_body())
    out = Path(__file__).resolve().parents[5] / ".issue-103-body.md"
    out.write_text(body, encoding="utf-8")
    print(f"patched body -> {out} ({len(body)} chars)")
    if dry:
        return 0
    subprocess.run(
        [
            "gh",
            "api",
            "-X",
            "PATCH",
            f"repos/{REPO}/issues/{ISSUE}",
            "--input",
            "-",
        ],
        input=json.dumps({"body": body}, ensure_ascii=False).encode("utf-8"),
        check=True,
    )
    print(f"updated https://github.com/{REPO}/issues/{ISSUE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
