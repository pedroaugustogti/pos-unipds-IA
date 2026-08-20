# Capacidade e velocity

## Time considerado

- 2 frontend senior
- 2 backend senior
- 1 DBA senior
- 1 arquiteto cloud AWS
- 1 QA

## Conversao para capacidade por sprint

Assumindo sprint de 2 semanas e foco senior:

- FE senior: 12 a 14 SP cada por sprint.
- BE senior: 12 a 14 SP cada por sprint.
- DBA senior: 6 a 8 SP por sprint.
- Arquiteto AWS: 4 a 6 SP por sprint.
- QA: suporte a validacao de 10 a 12 SP equivalentes, sem somar linearmente como coding capacity.

### Capacidade nominal bruta

- 2 FE x 13 SP = 26
- 2 BE x 13 SP = 26
- DBA = 7
- Arquiteto = 5

**Total bruto de construcao:** 64 SP teoricos.

### Ajustes de realidade

Aplicado buffer de 35% para:
- alinhamento entre repositorios,
- testes E2E em devices,
- revisoes tecnicas,
- validacoes de store e privacidade,
- carga de coordenacao e homologacao.

64 x 0.65 = **41.6 SP**

## Velocity de trabalho adotada

- **Faixa operacional:** 38 a 42 SP por sprint.
- **Valor de planejamento:** 40 SP/sprint.
- **Capacidade de 13 sprints:** 520 SP brutos planejaveis.

## Motivo da escolha

O projeto cruza mobile, API, compliance e operacao. Logo, a velocidade precisa refletir dependencia e validacao real, nao apenas capacidade de codificacao isolada.
