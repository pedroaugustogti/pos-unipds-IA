# 1.2 — Orquestração multi-agente (hub-and-spoke)

## Objetivo de aprendizado

Desenhar um sistema com **1 coordinator + N subagentes** em que ninguém “conversa de lado” e o coordinator é o único agregador.

## Analogia didática

**Redação de jornal**

- Editor-chefe (coordinator) recebe a pauta “investigar falha no checkout”
- Envia repórter web, repórter docs internos, analista de logs (subagentes)
- Repórteres **não se ligam** — entregam matéria ao editor
- Editor monta a matéria final / decide se precisa de mais uma rodada

Peer-to-peer (todos falam com todos) vira caos de estado — a prova prefere hub-spoke.

## Diagrama

```
                 ┌──────────────────────┐
     User ──────▶│     COORDINATOR      │
                 │  decompõe / agrega   │
                 │  escalate / stop     │
                 └──────────┬───────────┘
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ Sub: Web   │  │ Sub: Docs  │  │ Sub: Logs  │
     │ 2–3 tools  │  │ 2–3 tools  │  │ 2–3 tools  │
     └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
           │               │               │
           └───────────────┴───────────────┘
                           ▼
                    relatório(s) tipados
                           ▼
                      COORDINATOR
```

## Responsabilidades (decore)

| Papel | Faz | Não faz |
|-------|-----|---------|
| Coordinator | Decompor, delegar, rotear, agregar, escalate | Executar 18 tools sozinho |
| Subagente | Cumprir 1 job com poucas tools | Falar com outro subagente |
| Host | Spawn, timeouts, cancelamento | Inventar resultado se sub falhar |

## Exemplo prático — Multi-Agent Research (cenário de prova)

**Pedido do usuário:** “Por que a taxa de erro 5xx subiu 40% desde ontem? Relatório executivo.”

### Contrato do coordinator

```yaml
objetivo: relatorio_executivo_incidente
sucesso: causa_hipotese + evidencias + proximos_passos
budget:
  max_subagents: 3
  timeout_total_s: 180
stop:
  - user_cancel
  - budget_exhausted
  - evidencia_suficiente
escalate_se:
  - acesso_negado_em_2_fontes
  - conflito_irreconciliavel_entre_fontes
```

### Spawns (mesma “rodada” = concorrência)

```text
Task A — web_researcher
  objetivo: buscar status page / incidentes públicos últimos 2 dias
  allowedTools: [web_search, web_fetch]
  output: { findings: [...], sources: [...] }

Task B — docs_researcher
  objetivo: runbooks internos de checkout
  allowedTools: [search_kb, read_doc]
  output: { runbook_hits: [...], gaps: [...] }

Task C — logs_analyst
  objetivo: correlacionar 5xx por serviço
  allowedTools: [query_logs, get_service_health]
  output: { top_services: [...], spike_window: "..." }
```

### Agregação (coordinator)

```python
def aggregate(reports: list[dict]) -> dict:
    """Coordinator NÃO mistura tools dos subs — só sintetiza."""
    return {
        "hipotese": rank_causes(reports),
        "evidencias": flatten_sources(reports),
        "conflitos": find_conflicts(reports),
        "proximos_passos": suggest_actions(reports),
        "parcial": any(r.get("error") for r in reports),
    }
```

Se `logs_analyst` timeout:

- Coordinator marca `parcial=true`
- Continua com A+B
- Oferece escalate ou nova tentativa **só** no sub que falhou  
  (não mata A e B — anti-padrão de “abortar workflow inteiro”)

## Peer-to-peer vs hub-spoke (prova)

| Situação | Hub-spoke | Peer-to-peer |
|----------|-----------|--------------|
| Quem tem a verdade do estado? | Coordinator | Espalhada |
| Cancelamento | 1 ponto | Difícil |
| Tool explosion | Controlada por sub | Cada um acumula tools |
| Resposta típica CCAR-F | **Preferida** | Quase sempre errada |

## Mini-lab (20 min)

Desenhe no papel um hub-spoke para: “Preparar onboarding de cliente enterprise”.

1. Liste 3 subagentes com ≤3 tools cada  
2. Escreva o JSON de output de cada um  
3. Escreva 3 regras de escalate do coordinator  
4. Marque com X qualquer seta sub→sub (não pode existir)

## Checkpoint

- [ ] Explico hub-spoke em 30s
- [ ] Sei que subagentes não se comunicam
- [ ] Sei agregar com parcial em falha

← [1.1 Loop](./11-ciclo-agentic-loop.md) · [Índice](./ESTUDO.md) · → [1.3 Spawn](./13-spawn-e-contexto.md)
