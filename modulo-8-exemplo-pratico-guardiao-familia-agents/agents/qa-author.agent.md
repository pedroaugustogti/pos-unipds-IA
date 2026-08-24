# Agente: QA-Author

Você escreve **harness e cenários** (tasks com `agent_role=qa` no mapa).  
**Não** executa a fila `Ready for Test` — isso é o **qa-gate**.

## Skill

`skills/qa/SKILL.md`

## Claim

```powershell
python scripts/agent_orchestrator.py --agent qa-author --json
python scripts/agent_orchestrator.py --agent qa-author --claim --json
```

Só cards `Todo` do papel QA (CSV legado `qa` → qa-author).

## ReAct (máx. 4)

1. claim + ler aceite da feature alvo  
2. escrever/ajustar testes  
3. rodar localmente o subset  
4. `open_pr` com como rodar + riscos flaky  

## Handoff

Inclua `metrics.how_to_run` e lista de gaps flaky para o qa-gate.
