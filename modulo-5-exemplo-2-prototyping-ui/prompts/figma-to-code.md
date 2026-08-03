# PAPEL
Atue como um Engenheiro Front-End Sênior especializado em **Angular 21**, TypeScript e design systems bancários.

# OBJETIVO
Implementar o fluxo **Pix Agendado** como aplicação web a partir da especificação refinada do Exemplo 1, cobrindo caminho feliz e unhappy paths documentados.

# ENTRADA OBRIGATÓRIA
Anexe os artefatos listados em `docs/ENTRADA_EXEMPLO_1.md`:
- `fluxo-logico.mmd` — navegação
- `ui-states-checklist.md` — estados de UI
- `mensagens-ui.json` — copy i18n
- `edge-cases.md` — validações e erros

# STACK
- **Angular 21** (standalone components, signals, routing)
- CSS global mobile-first (max-width ~480px)
- Mock API com `Injectable` service + `localStorage`

# SCAFFOLD INICIAL
```bash
npx @angular/cli@21 new pix-app --directory app --style css --routing --skip-git --defaults --ssr=false
```

# ESTRUTURA ESPERADA
```
app/src/app/
├── core/
│   ├── models.ts
│   ├── messages.ts          # mensagens-ui.json
│   ├── mock-pix-api.service.ts
│   └── pix-state.service.ts
├── features/
│   ├── contacts/
│   ├── amount-date/
│   ├── review/
│   ├── receipt/
│   └── schedules/
└── app.routes.ts
```

# REGRAS DE NEGÓCIO
- Limite diário: R$ 5.000,00
- Não agendar para hoje (modal Pix imediato)
- MFA (senha `1234` na demo) antes de confirmar
- Idempotency key (`crypto.randomUUID()`) no POST

# CRITÉRIOS DE ACEITE
- [ ] Fluxo completo conforme Mermaid
- [ ] ≥ 3 unhappy paths de edge-cases.md
- [ ] Mensagens usando chaves de mensagens-ui.json
- [ ] `npm run build` sem erros
