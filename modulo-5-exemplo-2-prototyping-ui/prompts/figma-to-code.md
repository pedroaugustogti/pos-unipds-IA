# PAPEL
Atue como um Engenheiro Front-End Sênior especializado em React, TypeScript e design systems bancários.

# OBJETIVO
Implementar o fluxo **Pix Agendado** como aplicação web a partir da especificação refinada (sem Figma), cobrindo caminho feliz e unhappy paths documentados.

# ENTRADA OBRIGATÓRIA
Anexe ou leia os artefatos do Exemplo 1 (ver `docs/ENTRADA_EXEMPLO_1.md`):
- `fluxo-logico.mmd` — navegação
- `ui-states-checklist.md` — estados de UI
- `mensagens-ui.json` — copy i18n
- `edge-cases.md` — validações e erros

# STACK RECOMENDADA
- React 19 + Vite + TypeScript
- CSS modules ou CSS simples (mobile-first, max-width ~480px)
- Mock API local (sem backend real)

# REGRAS DE NEGÓCIO
- Limite diário: R$ 5.000,00
- Não agendar para hoje (sugerir Pix imediato)
- MFA (senha transacional) antes de confirmar
- Idempotency key no POST de agendamento
- Error Boundary no fluxo de confirmação

# FORMATO DE SAÍDA
Código em `app/` com estrutura:
```
app/
├── src/
│   ├── App.tsx
│   ├── constants.ts      # mensagens-ui.json
│   ├── api/mockPixApi.ts
│   └── components/
└── package.json
```

# CRITÉRIOS DE ACEITE
- [ ] Fluxo completo conforme Mermaid
- [ ] ≥ 3 unhappy paths de edge-cases.md
- [ ] Mensagens usando chaves de mensagens-ui.json
- [ ] Checklist ui-states-checklist.md revisado
