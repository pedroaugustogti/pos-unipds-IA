# ci — sinais de pipeline

| Módulo | Função |
|--------|--------|
| `ci_signals.py` | Eventos CI para o grafo |
| `ci_state.py` | Estado agregado CI |

Integração: sinais CI via `scripts/cli/ci_signal.py` → gateway; grafo v2 em `event_registry.py`.
