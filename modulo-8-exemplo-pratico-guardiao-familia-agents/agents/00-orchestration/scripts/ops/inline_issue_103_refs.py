#!/usr/bin/env python3
"""Remove refs .md que 404 no GitHub e inline conteúdo essencial na issue #103."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = "guardiaofamilia/guardiao-familia-child"
ISSUE = 103

SEC0_TABLE = """| Fase | Board Status | Agente | Responsabilidade | Proibido nesta fase |
|------|--------------|--------|------------------|---------------------|
| Claim | Todo → In Progress | **frontend-mobile** (creator) | Branch, implementar escopo sec. 3, testes unitários, RAG antes de codar | Review próprio código |
| Implementar | In Progress | **frontend-mobile** | `ChildHomeV2` + `dynamicGreeting()` + AC locais | Merge, QA Appium, fora do escopo |
| Review | In Code Review | **frontend-mobile-reviewer** | Review PR, testes saudação, `approve_review` / `request_changes` | Implementar feature, Appium |
| QA | In Test | **qa-gate** | MCP `qa_db_seed` → `qa_appium_suite_child` → evidências → `qa_db_cleanup` | Merge PR, alterar código |
| Merge | In Pull Request | **devops-cicd** | `merge_pr` após HITL | Alterar código da feature |"""

INLINE_APPENDIX = """
---

## Anexo A — Fluxo board (eventos)

| Evento | Status alvo | Quem dispara |
|--------|-------------|--------------|
| `claim` | In Progress | frontend-mobile |
| `open_pr` | Ready for Code Review | frontend-mobile |
| `start_review` | In Code Review | frontend-mobile-reviewer |
| `approve_review` | Ready for Test | frontend-mobile-reviewer |
| `request_changes` | In Progress | frontend-mobile-reviewer |
| `resubmit_review` | In Code Review | frontend-mobile (pós-correção) |
| `start_test` | In Test | qa-gate |
| `test_passed` | In Pull Request | qa-gate |
| `test_failed_bug` | In Progress | qa-gate |
| `merge_pr` | Done | devops-cicd |

## Anexo B — Papel `frontend-mobile` (resumo)

- Repo desta task: `guardiao-familia-child` · Metro **9090** · emulador **emulator-5556**
- Antes de codar: `query_mobile_flow_rag` (MCP) para fluxo 0→N e arquivos de tela
- Eventos MCP: `claim` → `open_pr` (ou `resubmit_review` após correções)
- Não executar QA Appium nem merge — handoff para reviewer e qa-gate
- Redirecionar: API/backend, infra, parent app, specs de teste → agentes correspondentes

## Anexo C — Papel `frontend-mobile-reviewer` (resumo)

- Assumir PR em **Ready for Code Review** (`start_review`)
- Validar escopo sec. 3, qualidade RN/TS, testes `childHome.state.test.ts` (3 períodos + bordas)
- `approve_review` → Ready for Test · `request_changes` → In Progress com comentários acionáveis
- Não implementar feature nem rodar Appium

## Anexo D — Papel `qa-gate` + evidências mobile (resumo)

**MCP (preferido):** `get_handoff` → `start_test` → `qa_db_seed` → `qa_appium_suite_child(from_db_seed=true)` → screenshots/MP4 → `qa_db_cleanup` → `test_passed` | `test_failed_bug`

**Stack:** Docker API/Postgres · emuladores 5554+5556 · `fast-stack.ps1` no mobile-setup · Appium dual

**Profile seed desta task:** `child_home` — API cria família+filho+código; Appium retoma após `paste_code_parent`

**Evidências obrigatórias (gate):**

| Artefato | Onde |
|----------|------|
| 3× PNG header | manhã 08h · tarde 15h · noite 21h (emulador-5556) |
| 3× MP4 | um por período (pairing→home ou jump de relógio na home) |
| JSON report | `agents/00-runtime/output/mobile/qa_evidence/T-P3-009/` |

**Marcadores de sucesso:** `fast-stack-last.json` → `ok: true` · log com `PAIRING_COMPLETE` / `SMOKE_CHILD_OK`

**Anti-patterns:** `test_passed` sem PNG/MP4 · Appium sem `APPS_READY_OK` · commitar `stage-handoff.json`

## Anexo E — Template PR (preencher no `open_pr`)

```markdown
## Resumo
**Task:** T-P3-009 — Child home: saudação dinâmica por horário no cabeçalho
**Agente:** frontend-mobile · **Repo:** guardiao-familia-child

## Estratégia
1. Centralizar `dynamicGreeting()` em `childHome.state.ts`
2. Header ChildHomeV2: `{dynamicGreeting()}, {nome}!`
3. Testes unitários 3 períodos + bordas 11:59/12:00 e 17:59/18:00

## Arquivos alterados
| Arquivo | Mudança |
|---------|---------|
| screens/ChildHomeV2.tsx | greeting no header |
| screens/childHome.state.ts | dynamicGreeting (se ajuste) |
| screens/__tests__/childHome.state.test.ts | casos manhã/tarde/noite |

## Test plan
- [ ] `npm test -- childHome.state` passa
- [ ] Validado emulador 5556 com hora 08/15/21h (screenshots no PR)
- [ ] Fluxo sec. 2.1 reproduzido antes do PR

## Board
- [ ] Issue T-P3-009 → Ready for Code Review
- [ ] Comentário sec. 10.1 na issue
```
"""


def fetch_body() -> str:
    raw = subprocess.check_output(
        ["gh", "api", f"repos/{REPO}/issues/{ISSUE}"],
        encoding="utf-8",
    )
    return json.loads(raw)["body"]


def patch(body: str) -> str:
    # Tabela sec. 0 — remover coluna Skill com paths .md
    start = body.find("| Fase | Board Status | Agente | Skill |")
    end = body.find("\n\nFluxo:", start)
    if start != -1 and end != -1:
        body = body[:start] + SEC0_TABLE + body[end:]

    body = body.replace(
        "Fluxo: [`STATEGRAPH_FLOW.md`](https://github.com/guardiaofamilia/pos-unipds-IA/blob/main/modulo-8-exemplo-pratico-guardiao-familia-agents/skills/_shared/STATEGRAPH_FLOW.md)\n",
        "Fluxo board: ver **Anexo A** (eventos) e sec. 8.\n",
    )

    body = body.replace(
        "> Regra: [`MOBILE_USER_FLOW_TEMPLATE.md`](https://github.com/guardiaofamilia/pos-unipds-IA/blob/main/modulo-8-exemplo-pratico-guardiao-familia-agents/board_automation/templates/MOBILE_USER_FLOW_TEMPLATE.md). Creator e qa-gate **seguem estes passos**.\n",
        "> Creator e qa-gate **seguem os passos abaixo** (user flow obrigatório: `app`, `entry_point`, `preconditions`, `steps`, `target_screen`, `target_element`, `emulator`, `metro_port`).\n",
    )

    body = body.replace(
        "- [ ] PR preenchido com `docs/templates/PR_TEMPLATE.md`",
        "- [ ] PR preenchido conforme **Anexo E** (template inline)",
    )

    body = body.replace(
        "| Skill | `modulo-8-.../agents/qa-gate/SKILL.md` · `MOBILE_SETUP_EVIDENCE.md` |",
        "| Referência QA | **Anexo D** (qa-gate + evidências mobile) |",
    )

    # Corrigir middle-dot residual
    body = body.replace(" Â· ", " · ")

    if "## Anexo A — Fluxo board" not in body:
        body = body.rstrip() + INLINE_APPENDIX

    return body


def main() -> int:
    dry = "--dry-run" in sys.argv
    body = patch(fetch_body())
    out = Path(__file__).resolve().parents[5] / ".issue-103-body-fixed.md"
    out.write_text(body, encoding="utf-8")
    print(f"patched {len(body)} chars -> {out}")
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
