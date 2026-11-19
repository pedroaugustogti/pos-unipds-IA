# Prova — D3 Claude Code (peso 20%)

Tempo sugerido: **20 min** · 10 itens.

## Cenario — Code Generation with Claude Code

Time usa Claude Code para features em monorepo. Ha `CLAUDE.md`, hooks de test
e politica que bloqueia push direto em `main`.

**Q1.** Onde documentar "nao adicionar dependencia sem perguntar"?
- A) So no chat
- B) Em `CLAUDE.md` do projeto
- C) No Dockerfile
- D) No billing da Anthropic

**Q2.** Melhor uso de plan mode:
- A) Refatoracao ampla em modulo de pagamentos
- B) Corrigir typo em comentario
- C) Sempre desligado
- D) So no CI

**Q3.** (multipla) Boas praticas de permissao:
- A) Deny `rm -rf` / force push
- B) Allowlist de diretorios editaveis
- C) Root shell em CI sem log
- D) Exigir testes apos Write

## Cenario — Claude Code for CI

Job gera review de PR e sugere testes.

**Q4.** Prompt de review deve:
- A) Ser vago ("melhore o codigo")
- B) Ser acionavel, citar arquivos e minimizar falso positivo
- C) Sempre aprovar
- D) Pedir fine-tune

**Q5.** Diff grande sem testes. Acao do pipeline?
- A) Merge automatico
- B) Falhar check / exigir testes ou justificativa
- C) Ignorar
- D) Subir temperature

**Q6.** Hook pos-edit que roda lint falhou. Correto?
- A) Ignorar falha
- B) Bloquear conclusao ate corrigir ou override explicito
- C) Remover lint do repo
- D) Trocar de modelo

**Q7.** Precedencia tipica de instrucoes de projeto:
- A) Chat solto > CLAUDE.md
- B) CLAUDE.md do projeto orienta o agente de forma persistente
- C) So settings globais do usuario
- D) README do GitHub Actions

**Q8.** Escopo de tarefa ruim:
- A) "Adicione validacao de e-mail no form X com testes"
- B) "Melhore o sistema inteiro"
- C) "Corrija o bug #123 reproduzido no log"
- D) "Gere teste para `parseInvoice`"

**Q9.** Em CI, Claude deve ter acesso a secrets de producao?
- A) Sim, sempre
- B) Nao — least privilege; secrets mascarados / ausentes
- C) So se pedir no prompt
- D) Sim via MCP publico

**Q10.** Verificar trabalho do Claude Code:
- A) Confiar no summary do modelo
- B) Diff + testes/lint independentes
- C) Contar linhas geradas
- D) Olhar so o titulo do commit

## Gabarito

1B · 2A · 3ABD · 4B · 5B · 6B · 7B · 8B · 9B · 10B

