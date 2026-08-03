# PAPEL
Atue como um Arquiteto de Soluções Sênior.

# OBJETIVO
Com base na análise de riscos e requisitos refinados (`docs/refinement/edge-cases.md`), criar um Diagrama de Fluxo (Flowchart) em **Mermaid.js**.

# ENTRADA
Use o contexto da conversa anterior ou cole o conteúdo de `edge-cases.md` antes de executar este prompt.

# REQUISITOS DO DIAGRAMA
1. **Orientação:** Top-Down (`graph TD`).
2. **Cobertura:** Caminho feliz (sucesso) e todos os caminhos infelizes (erros de API, validação, timeout, falta de saldo).
3. **Estados de interface:** Represente telas de *Loading*, *Empty State* e *Feedback de Erro*.
4. **Estilização semântica:**
   - Nós retangulares `[]` para ações do usuário ou processos do sistema.
   - Losangos `{}` para decisões de lógica de negócio.
   - Classes:
     - `classDef error fill:#f96,stroke:#333,stroke-width:2px;`
     - `classDef success fill:#9f6,stroke:#333,stroke-width:2px;`
     - `classDef uiState fill:#e1f5fe,stroke:#01579b,stroke-width:1px;`

# FORMATO DE SAÍDA
Apenas o código Mermaid (sem bloco markdown). Salve em `docs/refinement/fluxo-logico.mmd`.

# VALIDAÇÃO
Renderize em https://mermaid.live antes de versionar.
