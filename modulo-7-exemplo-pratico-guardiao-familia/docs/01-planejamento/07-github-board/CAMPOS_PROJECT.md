# Campos propostos para o GitHub Project

## Campos organizacionais ja disponiveis

- `Priority` (Urgent, High, Medium, Low)
- `Start date`
- `Target date`
- `Effort` (High, Medium, Low)

## Campos desejados para o modelo completo

- `OKR` (single select)
- `Epic` (single select)
- `Story Points` (number)
- `RICE Score` (number)
- `WSJF` (number)
- `Sprint` (iteration ou single select)
- `Release Blocker` (checkbox)

## Campo preservado

- `Onda` deve permanecer para rastreabilidade historica.

## Estrategia pratica neste ambiente

Como o GitHub MCP disponivel aqui exp?e escrita de issues, mas nao um conjunto completo de operacoes de Project V2, a estrategia imediata e:

1. Reescrever titulos e descricoes das issues-chave.
2. Ajustar `Priority`, `Effort`, `Start date` e `Target date` onde fizer sentido.
3. Usar a documentacao local como fonte de verdade para campos ainda nao automatizados (`OKR`, `RICE`, `WSJF`, `Sprint`).
4. Quando `gh` CLI ou automacao GraphQL estiver disponivel, propagar esses campos para o Project.
