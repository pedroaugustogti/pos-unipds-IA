# 3.4 — Plan mode vs execucao direta

## Objetivo
Escolher plan (explorar → plano → executar) vs direct (editar ja).

## Analogia
Planta aprovada vs trocar lampada.

## Matriz

| Situacao | Modo |
|----------|------|
| Multi-arquivo / arquitetural / ambiguo | **Plan** |
| Billing / auth / migracao | **Plan** |
| Arquivo unico, mudanca obvia | **Direct** |
| Typo / rename local | **Direct** |

## Exemplo
- Direct: "Em `utils/date.ts`, corrija timezone UTC-3"
- Plan: "Extraia pricing para package compartilhado sem quebrar API"

## Mini-lab
Classifique 5 pedidos do seu dia em plan vs direct.

## Checkpoint
- [ ] Criterio em 1 frase
- [ ] 2 exemplos de cada

← [3.3](./33-path-rules.md) · [ESTUDO](./ESTUDO.md) · → [3.5](./35-refinamento-iterativo.md)
