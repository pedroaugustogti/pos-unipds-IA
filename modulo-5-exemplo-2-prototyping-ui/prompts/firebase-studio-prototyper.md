# PAPEL
Atue como Product Designer e Prompt Engineer para o **Firebase Studio App Prototyping agent**.

# OBJETIVO
Gerar prompts iterativos para construir um protótipo web full-stack do fluxo **Pix Agendado**, validando contra a especificação do Exemplo 1.

# CONTEXTO (cole no primeiro prompt do Prototyper)
```
Feature: Pix Agendado em app bancário mobile-first.

Fluxo feliz:
1. Selecionar contato (ou buscar chave Pix)
2. Inserir valor (máx R$ 5.000/dia)
3. Escolher data futura (não permitir hoje)
4. Revisar dados
5. Confirmar com senha/biometria
6. Exibir comprovante
7. Listar e cancelar agendamentos

Unhappy paths obrigatórios:
- Lista de contatos vazia
- Valor acima do limite
- Data inválida / hoje → sugerir Pix imediato
- Erro de saldo na API
- Cancelamento bloqueado (já em processamento)
```

# PROMPTS ITERATIVOS (sugestão)

**Prompt 1 — estrutura:**
> Crie um app web mobile-first com telas: Contatos, Valor/Data, Revisão, Comprovante, Meus Agendamentos. Tema escuro, estilo banco digital.

**Prompt 2 — validações:**
> Adicione validação: valor > 5000 desabilita continuar; date picker só permite datas futuras; empty state na lista de contatos.

**Prompt 3 — erros:**
> Implemente modais de erro para: saldo insuficiente, falha de conexão, MFA incorreto. Use tom blameless.

**Prompt 4 — cancelamento:**
> Na lista de agendamentos, permita cancelar com loading no item e erro se já estiver em processamento.

# VALIDAÇÃO
Compare o protótipo gerado com `ui-states-checklist.md` do Exemplo 1 antes de publicar.

# REFERÊNCIA UNIPDS
- [Firebase Studio](https://firebase.google.com/docs/studio)
- [Builder.io + Figma import](https://firebase.blog/posts/2025/09/firebase-studio-builder-io-design-development/)
