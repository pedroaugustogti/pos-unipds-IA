# Lab — Evoluir o prompt do BragBot

Use este prompt no Cursor (ou edite `app/src/flows.ts` diretamente) para o Lab 4 da aula.

## Contexto

O flow `bragGeneratorFlow` em `app/src/flows.ts` transforma rascunhos informais em Brag Documents. O schema de saída está em `BragSchema`.

## Tarefa

Adicione uma **Regra 5** ao prompt do flow:

> Se o usuário não fornecer números ou percentuais explícitos, o campo `metrics` deve conter apenas descrições qualitativas (ex.: "latência reduzida", "menos incidentes em produção") — **nunca inventar percentuais ou valores numéricos**.

## Validação

1. Execute `npm run genkit:ui` em `app/`
2. Teste com input **sem métricas**:  
   `"Refatorei o módulo de pagamentos e a diretoria elogiou a clareza do código"`
3. Teste com input **com métricas**:  
   `"Reduzi a latência de 800ms para 120ms com cache Redis"`
4. Compare os arrays `metrics` nos dois casos

## Critério de aceite

- Input sem números → `metrics` sem valores inventados (ex.: sem "50%" se não foi mencionado)
- Input com números → `metrics` preserva os dados fornecidos

## Extensão (opcional)

Adicione campo `actionTaken` na UI de detalhe (`detail.component.ts`) — hoje o service mapeia apenas `context`, `impact` e `metrics`.
