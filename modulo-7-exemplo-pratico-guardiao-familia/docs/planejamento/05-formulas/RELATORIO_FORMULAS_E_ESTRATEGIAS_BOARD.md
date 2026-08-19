# Formulas e estrategias do board

## Quando usar cada framework

### RICE
Use para comparar valor relativo ao esforco quando houver mais de uma opcao funcional concorrendo por capacidade.

Formula:
`RICE = (Reach x Impact x Confidence) / Effort`

### WSJF
Use para decidir o que entra primeiro no sprint quando o custo do atraso e relevante.

Formula:
`WSJF = Cost of Delay / Job Size`

### PERT
Use para obter uma media ponderada de prazo por epico.

Formula:
`PERT = (O + 4M + P) / 6`

### Monte Carlo
Use para converter varias estimativas em probabilidade de prazo agregado.

## Estrategia de aplicacao no Guardiao Familia

1. OKR decide **por que** o item existe.
2. RICE ajuda a medir **quanto valor** o item tem.
3. WSJF decide **quando** o item entra.
4. PERT e Monte Carlo indicam **quao arriscado** e assumir a data.

## Campos obrigatorios do board

- Titulo reescrito para resultado observavel.
- OKR.
- Epic.
- Story Points.
- RICE Score.
- WSJF.
- Sprint.
- Release Blocker.
- Repo.
- Status.

## Regra de reescrita dos cards

Todo card deve responder a estas perguntas no titulo ou descricao:
- o que muda para o usuario ou operacao,
- qual repo principal executa,
- como validar pronto,
- se bloqueia release,
- a qual KR ele pertence.
