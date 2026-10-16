# Relatório Didático — Aspectos humanos e éticos

> Aula `modulo-10-exemplo-1-aspectos-humanos-eticos`  
> Caso: triagem de UTI por um algoritmo que maximiza vidas salvas e, na auditoria, rebaixa pacientes de baixa renda e minorias étnicas.

Fonte: [`Estudo_de_Caso_Responsabilidade_IA_Atualizado.pdf`](../../materiais_aula/Estudo_de_Caso_Responsabilidade_IA_Atualizado.pdf).

## Objetivo

Separar o que o modelo otimiza, o que ele aprendeu por proxy e quem responde pelo impasse entre eficiência e equidade.

## Cenário

Uma rede de hospitais públicos contrata um sistema para ordenar a fila de UTI e de exames de alta complexidade. O objetivo declarado é salvar mais vidas: priorizar quem tem maior risco de morte imediata e maior probabilidade estatística de recuperação. O treino usa o histórico clínico e de atendimento de milhões de pacientes ao longo de 10 anos.

## Conflito

Na validação, auditores veem pacientes de baixa renda e minorias étnicas em posições mais baixas da fila, com o mesmo quadro clínico e a mesma gravidade de pacientes de alta renda.

| Achado | Efeito |
|--------|--------|
| Cor da pele e renda foram removidas do conjunto inicial | O modelo não decide por essas colunas |
| CEP e hospital de origem ficaram | Viram proxy de renda e de território |
| Histórico das periferias | Menos exame preventivo, diagnóstico mais tardio, menos recurso para o pós-cirúrgico em casa |
| Cálculo do modelo | Região X sobrevive menos após a alta; para maximizar vidas com o recurso disponível, prioriza a região Y |

## Impasse

Penalizar as variáveis geográficas e socioeconômicas reduz a eficiência do hospital: estatisticamente, menos vidas totais ao final do ano. Manter o modelo perpetua e aprofunda a desigualdade que já estava nos dados.

## Camadas

| Camada | Artefato | Papel |
|--------|----------|-------|
| 1.1 Caso | `Estudo_de_Caso_Responsabilidade_IA_Atualizado.pdf` | Cenário, auditoria e impasse |
| 1.2 Leitura | [`RESPONSABILIDADE_IA.md`](./RESPONSABILIDADE_IA.md) | O que registrar do caso |
| 1.3 Debate | [`QUESTOES_PARA_DEBATE.md`](./QUESTOES_PARA_DEBATE.md) | Equidade, accountability e explicabilidade |

## Ponte

| Exemplo | Ligação |
|---------|---------|
| Ex.2 deste módulo | Dado recuperado não vira ordem; a responsabilidade continua humana |
| Guardião | [`../exemplo_real/01-guardiao/aplicacao.md`](../exemplo_real/01-guardiao/aplicacao.md) |
