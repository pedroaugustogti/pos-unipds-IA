# 4.2 — Few-shot prompting

## Objetivo
Usar 2–4 exemplos com **raciocinio**, nao so input/output mudos.

## Analogia
Aula com exercicio resolvido no quadro mostrando o **porquê**.

## Quando
Ambiguidade, formato, edge cases, reduzir alucinacao em extracao.

## Exemplo
```text
Exemplo 1:
Input: comentario "retorna nome completo" + codigo return user.firstName
Output: issue medium — comentario mente (so firstName)
Reasoning: contradicao factual comentario vs codigo

Exemplo 2:
Input: "valida input" + length > 0
Output: null
Reasoning: vago mas nao falso — nao flag
```

Sweet spot: **2–4** exemplos. Mais = overfitting + custo de contexto.

## Mini-lab
2 few-shots para classificar tickets billing vs shipping.

## Checkpoint
- [ ] Exemplos com reasoning
- [ ] Sei o sweet spot 2–4

← [4.1](./41-criterios-explicitos.md) · [ESTUDO](./ESTUDO.md) · → [4.3](./43-structured-output.md)
