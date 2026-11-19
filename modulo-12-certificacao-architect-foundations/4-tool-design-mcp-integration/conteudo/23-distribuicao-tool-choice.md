# 2.3 — Distribuicao de tools e tool_choice

## Objetivo
Manter ~4–5 tools quentes por agente; distribuir o resto em subagentes (ou tool search).

## Analogia
Mesa cirurgica: so instrumentos da cirurgia atual — resto na sala ao lado.

## Antes / depois
18 tools num agente → coordinator + Search(3) + Analysis(3) + Action(3) + Billing(3).

`tool_choice`: auto / any / tool / none (+ nota de modelos sem forced).  
`disable_parallel_tool_use` quando uma call por vez.

## Mini-lab
Parta lista de 12 tools em 3 agentes.

## Checkpoint
- [ ] Principio 4–5
- [ ] Sei quando parallel tools ajuda/atrapalha

← [2.2](./22-erros-estruturados.md) · [ESTUDO](./ESTUDO.md) · → [2.4](./24-mcp-config.md)
