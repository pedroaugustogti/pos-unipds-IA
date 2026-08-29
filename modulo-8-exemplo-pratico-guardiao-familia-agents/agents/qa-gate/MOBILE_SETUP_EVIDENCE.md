---
name: guardiao-qa-mobile-setup-evidence
description: >-
  Gera evidências PNG/MP4 e logs via guardiao-familia-mobile-setup (fast-stack + Appium).
  Obrigatório para tickets frontend-mobile em Ready for Test e regressão de pareamento.
---

# QA — Evidências mobile (Appium / mobile-setup)

**Fonte única de runtime E2E Android:** `guardiao-familia-mobile-setup`  
Path canônico: `C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-mobile-setup`  
Env: `GUARDAO_MOBILE_SETUP_PATH`

> Não usar `guardiao-familia-api/test/appium/` para novas evidências — engine migrado para mobile-setup (`appium/` + `scripts/fast-stack.ps1`).

Documentação da suite: `mobile-setup/docs/ESTRUTURA.md`.

## Quando aplicar

| Situação | Ação |
|----------|------|
| Ticket `frontend-mobile` ou PR em parent/child | **Obrigatório** anexar evidências antes de `test_passed` |
| Regressão pareamento (P0) | Fluxo `pairing` completo + MP4 se `video_mp4: true` no ticket |
| Alteração de tela específica | Feature/step Appium alinhado à tela (ver mapa abaixo) |
| Apenas harness Jest/API | Esta skill **não** substitui testes unitários |

Consultar plano de evidência: `crew/output/mobile_evidence_guide_merged.json` ou MCP `query_mobile_flow_rag` (`chunk_type=evidence_guide`).

## Stack que a suite sobe (automático)

```
Docker/API → emuladores dual (5554/5556) → Metro 8082/9090 → build APK → APPS_READY → Appium :4723 → feature
```

Orquestrador: `scripts/fast-stack.ps1` (idempotente — pula fases já UP).

## DB seed (evitar cadastro/pairing do zero)

Quando o ticket define `qa.db_seed.enabled: true`, o pipeline:

1. **Bootstrap** — Docker API/Postgres/Redis (`bootstrap_api_stack`)
2. **Seed API** — login parent → família → filho → `pairing-code` (`run_pairing_smoke_python`)
3. **Handoff** — grava `mobile-setup/docs/stage-handoff.json` com `lastStep` do profile
4. **Appium** — `-ResumeFromHandoff` ou `-PairingCycle` conforme profile
5. **Cleanup** — purge Postgres (`purge-appium-test-users.py`) + reset handoff (após evidências)

| Profile | O que pula | Appium flags |
|---------|------------|--------------|
| `pairing_warm` | `config_family` (família já na API) | `-PairingCycle` |
| `child_home` | cadastro + paste_code (retoma permissões→home) | `-ResumeFromHandoff` · `lastStep=paste_code_parent` |
| `permissions_resume` | até `allow_permissions` | `-ResumeFromHandoff` · `lastStep=allow_permissions` |

**Dependências:** Docker · `GUARDAO_MOBILE_SETUP_PATH` · emuladores 5554/5556 · `psycopg` (script purge) · Node (opcional, `reset-handoff-cycle.mjs`)

```yaml
# Exemplo no ticket (BACKLOG / agent-task JSON)
qa:
  db_seed:
    enabled: true
    profile: child_home
    family_name: "QA Evidence T-P3-009"
    child_name: "Filho QA T-P3-009"
    resume_after_step: paste_code_parent
    cleanup: true
    bootstrap_api: true
```

Cleanup manual: `python agents/qa-gate/scripts/mobile_e2e_seed.py --task T-XXX --cleanup-only`

## Comandos — módulo 8 (preferido)

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents

# Seed DB + handoff (pula cadastro manual — ver ticket qa.db_seed)
python agents/qa-gate/scripts/mobile_e2e_seed.py --task T-P04-001 --profile child_home

# Check + captura evidências para task (empacota em crew/output/evidence/{task_id}/)
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P04-001 --mode check

# Regressão pareamento completa (cold: sobe tudo)
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P04-001 --feature pairing --mode full

# Ciclo quente (emuladores já up, ~80s)
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P04-001 --feature pairing --mode cycle

# Tela/step isolado (stack já em APPS_READY_OK)
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P04-001 --feature copy_code_pairing --mode smoke --skip-build
```

Publicar na issue:

```powershell
python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-P04-001 --feature pairing --mode cycle --comment-issue
```

## Comandos — mobile-setup direto

```powershell
cd C:\Users\pedro\Documents\guardiao-familia\guardiao-familia-mobile-setup

# Primeira vez / stack fria
.\scripts\fast-stack.ps1

# Só Appium pairing (infra já up)
$env:GF_APPIUM_FEATURE = "pairing"
.\scripts\fast-stack.ps1 -Phase Smoke -SkipBuild

# Re-pareamento rápido
.\scripts\fast-stack.ps1 -PairingCycle -PairingLog docs\pairing-cycle-last.log
```

Features Appium (`GF_APPIUM_FEATURE` ou `--feature`):

| Feature | Uso típico |
|---------|------------|
| `create_account` | Cadastro parent (pré-requisito pairing) |
| `config_family` | Wizard família/filho |
| `pairing` | Golden flow parent↔child até ambas homes |
| `login` | Só autenticação parent |
| `copy_code_pairing` | Código 6 dígitos (Config → Gerir filhos) |
| `paste_code_parent` | Child cola código |
| `allow_permissions` | Permissões child |
| `go_to_home_child` / `go_to_home_parent` | Validação home |

## Artefatos de evidência (coletar sempre)

| Artefato | Path (relativo ao mobile-setup) | Conteúdo |
|----------|----------------------------------|----------|
| Relatório orquestrador | `docs/fast-stack-last.json` | Tempos por fase, ok/fail |
| Log Appium | `docs/appium-last.log` | Marcadores `PAIRING_COMPLETE`, steps |
| Timings por step | `docs/appium-step-timings.json` | Duração por feature/step |
| Run archivado | `docs/appium-runs/run-*.log` | Log completo da sessão |
| Análise erros | `docs/appium-runs/analysis-last.json` | Padrões recorrentes |
| Evidência visual (falha) | `docs/appium-evidence/{step}_{ts}/` | `screen.png`, `page-source.xml`, `meta.json` |
| Handoff E2E | `docs/stage-handoff.json` | **Não commitar** — só referência local |
| Pacote QA (módulo 8) | `crew/output/evidence/{task_id}/` | Cópia empacotada + `manifest.json` |

### PNG (aceite)

- **Por AC:** screenshot de cada tela tocada pelo fluxo — em falha automático em `appium-evidence/`; em sucesso usar `--record-screens` (script QA) ou captura manual `adb exec-out screencap`.
- **Mínimo gate:** 1 PNG parent + 1 PNG child no estado final (home ou tela alterada).

### MP4 (quando ticket pede `video_mp4: true`)

```powershell
# Parent (durante o fluxo Appium)
adb -s emulator-5554 shell screenrecord /sdcard/qa-parent.mp4
# ... executar fast-stack / pairing ...
adb -s emulator-5554 pull /sdcard/qa-parent.mp4 crew/output/evidence/T-XXX/parent-flow.mp4

# Child (pareamento P0)
adb -s emulator-5556 shell screenrecord /sdcard/qa-child.mp4
adb -s emulator-5556 pull /sdcard/qa-child.mp4 crew/output/evidence/T-XXX/child-flow.mp4
```

Ou: `python agents/qa-gate/scripts/qa_mobile_evidence.py --task T-XXX --feature pairing --mode cycle --record-video`

Limite ADB: ~3 min / arquivo; fluxos longos gravar por step.

## Fluxo QA Author (escreve harness)

1. Discovery: `python agents/qa-gate/scripts/qa_discover_mobile_flows.py --app both`
2. Guia evidência: arquivos static em `agents/00-runtime/output/mobile/guides/mobile_evidence_guide_*.json`
3. Implementar/ajustar spec se necessário — **execução E2E via mobile-setup**, não API repo
4. Rodar `qa_mobile_evidence.py` e anexar `manifest.json` ao PR

## Fluxo QA Gate (Ready for Test)

1. Ler handoff: `crew/output/handoffs/{task_id}.json` (PR + repo)
2. Se `repo` ∈ `{guardiao-familia-parent, guardiao-familia-child}` → **rodar evidência mobile**
3. Validar: `fast-stack-last.json` → `ok: true` e marcador `PAIRING_COMPLETE` no log (fluxo pairing)
4. Checar PNG/MP4 no pacote `crew/output/evidence/{task_id}/`
5. `test_passed` só com evidências anexadas à issue; senão `test_failed_bug` com paths dos logs

## Integração Python (agentes / LangGraph)

```python
from lib.mobile.qa_mobile_setup_evidence import run_mobile_evidence, collect_artifacts, format_evidence_comment

out = run_mobile_evidence(task_id="T-P04-001", feature="pairing", mode="cycle")
comment = format_evidence_comment(out)
```

Delegação baixo nível: `lib/mobile_setup_client.py` (`run_pairing`, `run_python`, `setup_root()`).

## Pré-requisitos

- `GUARDAO_MOBILE_SETUP_PATH` apontando para o clone local
- `appium/npm install` já feito em `mobile-setup/appium`
- Docker + Android SDK (`ANDROID_HOME`) — ver `docs/operacao/LOCAL_E2E_MOBILE.md`
- Junctions: `mobile-setup/agents/qa-gate/scripts/mobile_short_paths.ps1`

## Anti-patterns

- Marcar `test_passed` sem PNG quando ticket mobile exige evidência visual
- Rodar `appium/*/run.mjs` sem `fast-stack` (sem `APPS_READY_OK`)
- Commitar `stage-handoff.json` (contém credenciais de teste)
- Usar emulador single para fluxos pairing dual sem `-Single` explícito e aceite documentado

## Palavras-chave

`evidência`, `screenshot`, `screenrecord`, `appium`, `mobile-setup`, `fast-stack`, `pairing-cycle`, `frontend-mobile`, `E2E Android`
