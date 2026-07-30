# Mapeamento de Conceitos — Nosso Framework vs Mercado

| Nosso framework | LangChain | LangGraph |
|-----------------|-----------|-----------|
| `agent.md` | prompt template | system message |
| `skills.md` | `@tool` decorators | tool nodes |
| `architectures/react/planner.md` | `create_react_agent()` | ReAct node |
| `architectures/plan_execute/planner.md` | planner chain | `planejar` node |
| `architectures/reflect/critic.md` | evaluator chain | `avaliar` node |
| `ciclo.py` | `AgentExecutor` | `StateGraph` |
| `rules.md → max_etapas` | `max_iterations` | `recursion_limit` |
| `hooks.md → log` | `verbose=True` | callbacks |
| `circuit_breaker` | `handle_parsing_errors` | conditional edges |
| `trace.json` | callbacks / LangSmith | checkpointer |
| `evals/suites/*.yaml` | LangSmith evaluators | LangGraph eval harness |

> Mesmo conceito, representacao diferente: contrato Markdown vs codigo Python.
