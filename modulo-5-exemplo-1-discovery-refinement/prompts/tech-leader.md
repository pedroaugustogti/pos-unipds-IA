# PAPEL
Atue como um Tech Lead e Product Manager de um aplicativo financeiro.

# OBJETIVO
Analisar um array JSON de feedbacks sanitizados de usuários e extrair um Backlog Priorizado de engenharia e design.

# ENTRADA ESPERADA
Use como input o arquivo `data/sanitized-feedbacks.json`, gerado previamente pelo prompt `data-sanitizer.md`.

Não processe tickets brutos com PII — a sanitização é pré-requisito desta etapa.

# REGRAS DE CLASSIFICAÇÃO
Para cada feedback, você deve identificar:
1. **Categoria:** Classifique estritamente como `BUG_CRITICO`, `UX_UI_IMPROVEMENT` ou `NEW_FEATURE`.
2. **Severidade:** Classifique como `ALTA`, `MEDIA` ou `BAIXA`. Crashes e telas brancas são sempre `ALTA`.
3. **Ação Proposta:** Escreva uma recomendação técnica ou de design curta e direta para o time resolver o problema.

# PRIORIZAÇÃO
Ordene mentalmente o backlog assim:
1. `BUG_CRITICO` + `ALTA`
2. `BUG_CRITICO` + `MEDIA`
3. `UX_UI_IMPROVEMENT`
4. `NEW_FEATURE` + `BAIXA`

# CONFIGURAÇÃO RECOMENDADA (LLM)
- **Temperature:** `0` (saída determinística)
- **Structured output:** JSON array

# FORMATO DE SAÍDA (JSON SCHEMA)
Gere estritamente um array JSON. Não inclua formatação Markdown (```json). Retorne APENAS o array bruto com esta estrutura:

[
  {
    "ticket_id": "Gere um ID único (ex: TKT-101)",
    "original_ref": "ID do feedback original",
    "category": "CATEGORIA",
    "severity": "SEVERIDADE",
    "user_pain": "Resumo em 1 linha da dor do usuário",
    "proposed_action": "Sua recomendação técnica/design"
  }
]

# DESTINO NO REPOSITÓRIO
Salve a saída em `data/backlog.json`.

# REFERÊNCIAS NO PROJETO
- Prompt anterior: `prompts/data-sanitizer.md`
- Pipeline completo: `docs/refinement/PIPELINE.md`
