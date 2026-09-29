# Artefato de aula — gate de fine-tuning (Amplitude Auto e Saúde)

Decisão que libera (ou segura) o fine-tuning dos dois domínios da Amplitude. Ferramenta: `materiais_aula/decision_framework_tool.py`.

Regra do checklist (`materiais_aula/decision-framework-checklist.md`): a Pergunta 0 vem antes. Nas quatro seguintes, **uma vermelha basta** para não treinar. Limiar do score verde: **0,60**.

## Checklist — Amplitude Auto

Tarefa: extrair `segurado`, `placa`, `valor` de orçamento de oficina.

| # | Pergunta | Resposta | Veredito |
|---|----------|----------|----------|
| 0 | É conhecimento (fato que muda) ou comportamento (formato estável)? | O fato (nome, placa, valor) vem do documento da vez. O que se quer ensinar é o **formato JSON**, sempre igual. | **Segue** para as 4 perguntas. Não é caso de RAG. |
| 1 | A tarefa é estreita e repetida? | Uma frase cobre quase todo caso: orçamento de oficina → 3 campos. Score alto. | **Verde** |
| 2 | Já esgotou prompt + RAG + roteamento? | Mesmo prompt e o mesmo processo de validação já foram testados. Em escala (~8.000/mês) o status quo continua caro. | **Verde** |
| 3 | Tem dado suficiente, diverso e de qualidade? | Há histórico real de orçamentos com entrada e saída correta. p3 acima de 0,60. | **Verde** |
| 4 | O schema é estável o bastante? | O contrato com o sistema de sinistros não muda toda semana. | **Verde** |

**Veredito do caso:** 4× verde (composto **0,88**). **Fine-tuning vale a pena.** NPV ~R$ 4,8 mil em 24 meses, breakeven no mês 10. Próximo passo: dataset (Ex.2) → job (Ex.3) ou LoRA (Ex.4).

## Checklist — Saúde Empresarial

Tarefa: extrair `beneficiário`, `procedimento`, `valor` de recibo/clínica.

| # | Pergunta | Resposta | Veredito |
|---|----------|----------|----------|
| 0 | Conhecimento ou comportamento? | Igual ao Auto: o valor sai do recibo; o modelo precisa do **formato** fixo. | **Segue** para as 4 perguntas. |
| 1 | Tarefa estreita e repetida? | Recibo/clínica → 3 campos, o mesmo contrato na linha. | **Verde** |
| 2 | Esgotou prompt + RAG? | Mesmo processo do Auto, já testado. | **Verde** |
| 3 | Dado suficiente? | Volume histórico ainda curto. p3 = **0,35** (abaixo de 0,60). | **Vermelho** |
| 4 | Schema estável? | Contrato de saída com sinistros é fixo. Gate LGPD (dado sensível) passa com DPA; não é o que reprova. | **Verde** |

**Veredito do caso:** reprovado **só na p3**. **Não treinar agora.** Real Options: esperar ~9 meses acumulando dado (valor de esperar ~R$ 230). O Ex.3 reabre o **mesmo** critério, sem mudar a regra.

## Checklist — Atendimento (terceiro caso da aula)

Tarefa: negociar contestações abertas.

| # | Pergunta | Resposta | Veredito |
|---|----------|----------|----------|
| 0 | Conhecimento ou comportamento? | A resposta muda com a regra e o caso. Não há um formato único. | Já aponta **prompt + RAG**. |
| 1 | Tarefa estreita e repetida? | “Às vezes acolhe, às vezes recusa, às vezes pede documento.” | **Vermelho** |
| 2 | Esgotou prompt + RAG? | O gargalo não é escala de um schema; o prompt estruturado ainda é o caminho. | Não salva o gate. |
| 3 | Dado suficiente? | Histórico de sobra (p3 = **0,92**). | **Verde** — e mesmo assim não treina |
| 4 | Schema estável? | Cada contestação pede um desfecho diferente. Sem contrato único. | **Vermelho** |

**Veredito do caso:** p1 e p4 vermelhas. **Continue com prompt + RAG.** Dado não compensa tarefa aberta.

## Contrato de saída do modelo (os dois domínios)

Não misturar campos.

```json
{"dominio":"auto","schema":{"segurado":"string","placa":"string","valor":"number"}}
{"dominio":"saude","schema":{"beneficiario":"string","procedimento":"string","valor":"number"}}
```

## O que este artefato não faz

Não sobe peso nenhum. Só registra **se** treinar. O treino começa no dataset do Ex.2 e no job/adapter dos Ex.3–4.

Relatório da aula: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
