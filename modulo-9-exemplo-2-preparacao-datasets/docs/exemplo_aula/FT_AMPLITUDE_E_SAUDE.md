# Artefato de aula — datasets de fine-tuning (Amplitude Auto e Saúde)

O gate do Ex.1 aprovou Auto e segurou Saúde até haver dado. Estes arquivos são a **mesma história de 9 documentos**, melhorada etapa a etapa, para importar depois no job de API (Ex.3) ou no LoRA local (Ex.4). Ferramentas de referência em `../../materiais_aula/`: relevância, extração, gate de PII, limpeza.

Os quatro documentos reais da aula (`documentos-brutos/` e `dataset-amplitude-seguros.jsonl`) continuam sendo a extração publicada. A sequência abaixo é a versão didática, pequena o bastante para ler linha a linha.

## Schema — o que o fine-tuning vai cobrar

Definido antes de limpar, nos dois domínios, sem misturar campos.

| Caso (`metadata.caso`) | Instrução | Campos obrigatórios | Tipos |
|------------------------|-----------|---------------------|--------|
| `amplitude-auto` | Extraia segurado, placa e valor do orçamento de oficina | `segurado`, `placa`, `valor` | string, string, number |
| `amplitude-saude-empresarial` | Extraia beneficiário, procedimento e valor do recibo médico | `beneficiario`, `procedimento`, `valor` | string, string, number |

Passos da definição:

1. Uma frase descreve a tarefa (pergunta 1 do Ex.1). Se a frase muda por caso, o schema ainda não existe.
2. Cada domínio ganha a sua lista de campos. Auto não carrega `procedimento`; Saúde não carrega `placa`.
3. `valor` sai de texto brasileiro (`R$ 3.210,50`) para número (`3210.5`). Vazio, zero ou NaN invalida o exemplo.
4. O envelope canônico desta aula é `instrucao`, `entrada`, `saida`, `metadata`. O Ex.3 não lê esse envelope: traduz para `contents` / `role` / `parts` (arquivo 06).
5. `validar_exemplo` em `extraction_to_jsonl_tool.py` recusa linha sem campo obrigatório. Essa linha não segue no pipeline.

## Ordem dos arquivos

| Arquivo | Linhas | O que muda em relação ao anterior |
|---------|--------|-----------------------------------|
| [`01-dataset-bruto.jsonl`](./01-dataset-bruto.jsonl) | 9 | OCR cru. Sem par pergunta/resposta. |
| [`02-dataset-formalizado.jsonl`](./02-dataset-formalizado.jsonl) | 8 | Schema aplicado. Flyer fora. Incompleto ainda está marcado. |
| [`03-dataset-pii-redigido.jsonl`](./03-dataset-pii-redigido.jsonl) | 7 | CPF válido redigido. Nome permanece, porque é o rótulo. |
| [`04-dataset-deduplicado.jsonl`](./04-dataset-deduplicado.jsonl) | 5 | Quase-duplicatas fora. |
| [`05-dataset-ideal.jsonl`](./05-dataset-ideal.jsonl) | 4 | Fonte dominante limitada e distrator no texto. |
| [`06-dataset-ideal-vertex.jsonl`](./06-dataset-ideal-vertex.jsonl) | 4 | Os mesmos 4 exemplos no schema da API. Import do Ex.3 / FT local depois da conversão MLX. |

### 01 — bruto

Nove textos: dois orçamentos Auto da Oficina Estrela, a reimpressão do mesmo sinistro do Marcos, um da Silva, um sem placa, um folheto de promoção (não é sinistro), dois recibos de Carlos (original e cópia) e um do Lab Norte. Dois documentos trazem o CPF de teste da aula, `111.444.777-35`.

Ainda não serve para treinar. Não há `saida`.

### 02 — formalizado

O gate de relevância tira o folheto (sem ground truth, não é produção de sinistro). Os outros entram no envelope.

Melhoria: cada linha tem instrução, texto e JSON de saída. A linha `b05` (Paulo, sem placa) fica com `metadata.valido: false` e o erro `campo obrigatório ausente: placa`. Ela existe aqui para o defeito ser visível. Não entra nas etapas seguintes.

### 03 — PII redigido

Sai a linha inválida. Onde o CPF de teste era válido (dígito do Módulo 11), o texto vira `[CPF_REDIGIDO]`. Placa e valor ficam: não são o identificador que o gate remove.

O nome **não** é apagado. No demo de `pii_scrubbing_gate_tool.py` o nome some porque o artefato é o documento solto. No par de treino o nome é a resposta de `segurado` / `beneficiario`. Redigir a entrada e manter o nome na saída quebra o exemplo. O que sai é o identificador que **não** faz parte do schema (CPF).

### 04 — sem quase-duplicata

Saem `b02` (reimpressão do Marcos, mesma placa e mesmo valor) e `b08` (cópia do recibo do Carlos). MinHash+LSH na aula faz isso em escala; aqui o par está marcado em `metadata.quaseDuplicataDe`.

Ficam 3 Auto e 2 Saúde. A Oficina Estrela ainda aparece duas vezes (Marcos e Camila).

### 05 — ideal para o treino desta aula

O balanceamento por temperatura (α≈0,3 no tool) limita a fonte que domina. Neste conjunto mínimo, a Oficina Estrela fica com 1 exemplo (`b03` da Camila sai). Resultado: 2 Auto (Estrela e Silva) e 2 Saúde (Vida Nova e Lab Norte).

Cada `entrada` ganha uma linha distratora (`Franquia` ou `Coparticipação`) com outro valor. A `saida` continua o valor do reparo ou do procedimento, não o primeiro número do texto.

### 06 — schema da API

Tradução, não uma limpeza nova. `instrucao` + `entrada` viram o turno `user`; `saida` vira o texto JSON do turno `model` (`contents` / `parts`). É o arquivo que um job Vertex ou o conversor do Ex.4 pode ler.

Volume do piloto real (Ex.3), depois desta higiene em escala: **120 Auto + 80 Saúde**. Saúde só entra no job quando a reavaliação do Ex.1 passa.

Relatório da aula: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
