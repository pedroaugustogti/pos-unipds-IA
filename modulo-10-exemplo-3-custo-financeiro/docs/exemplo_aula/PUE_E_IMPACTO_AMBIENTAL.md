# PUE e impacto ambiental — escala nacional

O **PUE** (*Power Usage Effectiveness*, em português: efetividade do uso de energia) mede quanto da energia do data center realmente alimenta os servidores de TI. Quanto mais perto de 1,0, menos refrigeração e infra “morta”. Este relatório aplica a fórmula a um cenário mínimo de sistema nacional e traduz o overhead em custo e em equivalente de desmatamento (ordem de grandeza didática).

Leitura: `[CUSTO_FINANCEIRO.md](./CUSTO_FINANCEIRO.md)` · `[DILEMA_ECONOMICO_IA.md](./DILEMA_ECONOMICO_IA.md)`.  
Fonte da definição: [Nature — npj Clean Water](https://www.nature.com/articles/s41545-021-00101-w). Mapas: `[materiais_aula](../../materiais_aula/README.md)`.

## Definição e fórmula

**PUE** = *Power Usage Effectiveness* (efetividade do uso de energia).

```text
PUE = energia total da instalação
      ÷ energia só dos equipamentos de TI
```


| Valor     | Leitura                                                    |
| --------- | ---------------------------------------------------------- |
| **1,0**   | Ideal: toda a energia vai para TI                          |
| **> 1,0** | O excedente é refrigeração, iluminação, UPS, rede elétrica |
| Regra     | Quanto menor o PUE, melhor                                 |


Exemplo: TI usa 100 kWh e a instalação inteira 150 kWh → PUE = 1,5. Um terço da energia não calcula token; só mantém a sala fria e ligada.

## Cenário — infraestrutura mínima em escala nacional

Hipótese de produto: assistente com RAG para serviço público digital no Brasil (consulta, orientação, triagem). Números são **ordem de grandeza para aula**, não orçamento de edital.


| Parâmetro                 | Valor assumido                                                       |
| ------------------------- | -------------------------------------------------------------------- |
| Usuários ativos / mês     | 30 milhões                                                           |
| Consultas / usuário / mês | 3                                                                    |
| Requests / mês            | 90 milhões                                                           |
| Serving                   | Inferência + embedding + cache (não treina foundation model no site) |
| Frota mínima de TI        | 20 racks/nós de GPU para inferência + 10 nós CPU/storage/RAG         |
| Potência média de TI      | **100 kW** contínuos (média anual, com folga de pico)                |
| Energia anual de TI       | `100 kW × 8.760 h = 876.000 kWh/ano`                                 |


### CapEx mínimo (ordem de grandeza)


| Item                          | Estimativa                     |
| ----------------------------- | ------------------------------ |
| Nós GPU (20) + rede/storage   | R$ 6–10 milhões                |
| Instalação, rack, UPS parcial | R$ 1–2 milhões                 |
| **CapEx total (faixa)**       | **~R$ 8–12 milhões** (uma vez) |


### OpEx energético — dois PUEs

Mesma carga de TI (876.000 kWh/ano). Muda só a eficiência da instalação.


| Cenário                      | PUE     | Energia total (kWh/ano)     | Overhead = total − TI | Tarifa* R$/kWh | Conta energia / ano |
| ---------------------------- | ------- | --------------------------- | --------------------- | -------------- | ------------------- |
| DC eficiente (hyperscale)    | **1,2** | `876.000 × 1,2 = 1.051.200` | 175.200               | 0,80           | **R$ 840.960**      |
| DC típico empresarial        | **1,5** | `876.000 × 1,5 = 1.314.000` | 438.000               | 0,80           | **R$ 1.051.200**    |
| DC antigo / mal dimensionado | **1,8** | `876.000 × 1,8 = 1.576.800` | 700.800               | 0,80           | **R$ 1.261.440**    |


Tarifa comercial ilustrativa (~R$ 0,80/kWh). Ajuste com o contrato real e com [Electricity Maps](https://app.electricitymaps.com/).

Aplicação da fórmula (DC típico):

```text
PUE = 1.314.000 ÷ 876.000 = 1,5
```

## Comparativo de uso e financeiro


| Dimensão                    | PUE 1,2      | PUE 1,5      | Diferença                                                  |
| --------------------------- | ------------ | ------------ | ---------------------------------------------------------- |
| Energia que “trabalha” (TI) | 876.000 kWh  | 876.000 kWh  | Igual — mesma capacidade de servir requests                |
| Energia gasta em infra      | 175.200 kWh  | 438.000 kWh  | **+262.800 kWh/ano** no PUE 1,5                            |
| Conta de energia            | R$ 840.960   | R$ 1.051.200 | **+R$ 210.240/ano** (~25% a mais)                          |
| CapEx de GPU                | Mesmo        | Mesmo        | PUE não compra chip; compra refrigeração                   |
| Capacidade de atendimento   | 90 M req/mês | 90 M req/mês | Uso de produto igual; custo ambiental e elétrico diferente |


### Alternativa só API (OpEx puro)

Mesmo volume, sem frota própria: fatura de tokens (OpenAI/Gemini/Bedrock). Ordem de grandeza: dezenas a centenas de milhares de dólares por mês em pico nacional, conforme modelo e tamanho de prompt. Não há PUE seu — o overhead fica no data center do provedor (`[MODELO_BASEADO_EM_API.md](./MODELO_BASEADO_EM_API.md)`). O PUE entra quando você (ou o provedor) opera a instalação.

## Impacto em carbono e equivalente de desmatamento

Premissas explícitas (didáticas):


| Premissa                                              | Valor                           | Nota                                                                                 |
| ----------------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------ |
| Intensidade de carbono da rede                        | **0,08 kg CO₂e / kWh**          | Ordem típica do SIN brasileiro (hidro dominante); confira no Electricity Maps do mês |
| Sequestro anual de 1 árvore                           | **20 kg CO₂e / ano**            | Ordem de grandeza; varia com espécie e idade                                         |
| Sequestro anual de 1 ha de floresta em regeneração    | **5 t CO₂e / ano** (= 5.000 kg) | Ordem de grandeza; não substitui inventário de carbono                               |
| Estoque (evitar desmate de 1 ha de floresta tropical) | **~500 t CO₂e**                 | Carbono estocado convertido; ordem de grandeza                                       |


### Cálculo — energia total e só o overhead (PUE 1,5)


| Base                      | kWh/ano     | CO₂e (kg/ano) | Árvores-ano* | Hectares-ano† | Hectares de estoque‡ |
| ------------------------- | ----------- | ------------- | ------------ | ------------- | -------------------- |
| Só TI                     | 876.000     | 70.080        | 3.504        | 14,0          | 0,14                 |
| Instalação PUE 1,5        | 1.314.000   | 105.120       | 5.256        | 21,0          | 0,21                 |
| **Só overhead (PUE − 1)** | **438.000** | **35.040**    | **1.752**    | **7,0**       | **0,07**             |


 `kg CO₂e ÷ 20`  
 `kg CO₂e ÷ 5.000`  
 `kg CO₂e ÷ 500.000` — “equivalente de estoque”, não área desmatada no ano

### Comparativo PUE 1,2 vs 1,5 (só overhead)


|                          | PUE 1,2 | PUE 1,5 | Extra do PUE pior |
| ------------------------ | ------- | ------- | ----------------- |
| Overhead (kWh/ano)       | 175.200 | 438.000 | +262.800          |
| CO₂e (kg/ano)            | 14.016  | 35.040  | **+21.024**       |
| Árvores-ano              | 701     | 1.752   | **+1.051**        |
| Hectares-ano (sequestro) | 2,8     | 7,0     | **+4,2**          |


Leitura: com a **mesma** capacidade nacional de TI, piorar o PUE de 1,2 para 1,5 é como pedir ~1.000 árvores a mais por ano só para refrigerar e iluminar — ou ~4 hectares a mais de floresta em regeneração, em sequestro anual. O estoque de 0,07 ha no overhead do PUE 1,5 mostra que o carbono “queimado” em um ano ainda é pequeno frente a um hectare de floresta madura; o ponto da aula é a **proporção**: eficiência da instalação multiplica o impacto sem acrescentar um único request ao cidadão.

## O que a governança faz com isso


| Decisão                                                | Efeito no PUE / impacto                                               |
| ------------------------------------------------------ | --------------------------------------------------------------------- |
| Escolher região e provedor com PUE baixo e grade limpa | Menos kg CO₂e por kWh e menos overhead                                |
| Routing + RAG eficiente + caching                      | Menos kW de TI para o mesmo serviço → base do PUE cai                 |
| Quantização / serving certo                            | Menos GPU ociosa → menos energia de TI                                |
| Medir PUE e publicar                                   | Soft law vira número; hard law e compras públicas podem exigir o dado |


Relatório da aula: `[RELATORIO_DIDATICO_AULA.md](./RELATORIO_DIDATICO_AULA.md)`.