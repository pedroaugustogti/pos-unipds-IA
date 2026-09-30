# Etapa 4 — prompt pack no lugar do adapter (Guardião M8)

LoRA no Guardião seria um adapter de **formato** (plano, evidência JSON), nunca dos pesos do código. Enquanto o RAG resolver, o “adapter” é a skill versionada.

## Analogia operacional

| LoRA Amplitude | Guardião |
|----------------|----------|
| `adapters.safetensors` pequeno, base intacta | `SKILL.md` + `agent.md` versionados, modelo base intacto |
| Rank baixo primeiro | Skill curta primeiro. O builder já corta em ~3500 / ~2000 caracteres |
| Vários ranks no mesmo base | Vários papéis no mesmo LLM, cada um com a sua skill |
| Remover o adapter volta ao base | Tirar o papel do roteamento volta ao comportamento sem aquela política |

## Quando reconsiderar um adapter de verdade

Só se, depois do corpus do Ex.2 e do prompt do Ex.3, o eval do Ex.5 mostrar falha **de formato** repetida (JSON de evidência/plano) e não falha de retrieval. Aí o adapter é estreito e descartável.

Contexto: [`APLICACAO_M9_EX4_AO_GUARDIAO_M8.md`](./APLICACAO_M9_EX4_AO_GUARDIAO_M8.md)
