# Próxima Aula — Módulo 5, Exemplo 3: OpenSpec + CFP

> **Scaffold criado:** [`modulo-5-exemplo-3-openspec-cfp`](../../modulo-5-exemplo-3-openspec-cfp/) (via delivery-agent)

Plano de aula para continuidade do módulo **Ferramentas de IA para UI/UX**, após conclusão do [Exemplo 2 (Prototyping UI)](../README.md).

**Referência UNIPDS:** [modulo-03 — CFP Platform + OpenSpec](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-03)

---

## Contexto pedagógico

| Aula anterior | Esta aula | Próxima (UNIPDS) |
|---------------|-----------|------------------|
| Ex. 1 — Discovery/refinement (specs, edge cases, Mermaid) | **Ex. 3 — OpenSpec + CFP** (spec-driven com CFP Platform) | Ex. 4 — Cypress + OpenSpec (testes E2E) |
| Ex. 2 — Prototyping UI (Figma/Stitch → Angular 21) ✅ | | Ex. 5 — AI Integration (Firebase AI Logic) |

**Ponte com o Ex. 2:** o app `pix-app` já existe; nesta aula o aluno usa **agentes CLI** para refatorar, corrigir e evoluir o código gerado por IA — espelhando o fluxo real de equipes que prototipam com Cursor/Figma e depois consolidam com ferramentas de linha de comando.

---

## Objetivos de aprendizagem

Ao final da aula, o aluno será capaz de:

1. Configurar e usar **Gemini CLI** (ou agente CLI equivalente) no contexto do projeto Angular
2. Aplicar prompts de **refatoração segura** (escopo mínimo, diff revisável)
3. Executar tarefas de manutenção no `pix-app`: lint, testes, extração de componentes, remoção de código morto
4. Comparar **Cursor Agent** vs **CLI agent** para o mesmo problema (ex.: `correcao_css.md`)
5. Documentar mudanças com evidências de aceite (build + test)

---

## Pré-requisitos

- Exemplo 2 concluído ([`EVIDENCIAS_ACEITE.md`](EVIDENCIAS_ACEITE.md) ✅)
- Node.js 22+, Angular CLI 21
- Gemini CLI instalado (`npm i -g @google/gemini-cli` ou conforme doc UNIPDS)
- Repositório clonado com `pix-app` buildando

---

## Estrutura sugerida do repositório local

```
modulo-5-exemplo-3-openspec-cfp/
├── README.md
├── prompts/
│   ├── refactor-safe.md          # system: diff mínimo, sem over-engineering
│   ├── dead-code-cleanup.md      # remover scaffold legado
│   └── test-gap-fixer.md         # aumentar cobertura de testes
├── docs/
│   ├── ROTEIRO_AULA.md
│   └── EVIDENCIAS_ACEITE.md
└── alvo/                         # symlink ou cópia do pix-app do Ex. 2
    └── app/
```

> Na primeira turma, pode-se trabalhar **diretamente** em `modulo-5-exemplo-2-prototyping-ui/app/` sem criar pasta nova.

---

## Roteiro da aula (~2h)

### 1. Recapitulação (15 min)

- Demo rápida do Ex. 2: `/pix`, `/extrato`, `/comprovante`
- Revisar [`EVIDENCIAS_ACEITE.md`](EVIDENCIAS_ACEITE.md) — o que a IA gerou bem e o que ainda precisa de humano
- Conceito: **prototipação ≠ produção** — agents CLI entram na fase de consolidação

### 2. Setup Gemini CLI (20 min)

```bash
cd modulo-5-exemplo-2-prototyping-ui/app
gemini --version   # ou ferramenta indicada pelo UNIPDS
npm run build && npm test -- --watch=false
```

- Configurar contexto do projeto (`.gemini/` ou `GEMINI.md` conforme material UNIPDS)
- Regra de ouro: **sempre** `build` + `test` após cada refatoração

### 3. Laboratório 1 — Limpeza de código morto (25 min)

**Problema:** pasta `features/` do scaffold inicial não é usada nas rotas.

**Prompt sugerido:**
```
Analise app/src/app e remova apenas código morto não referenciado em rotas ou imports.
Não altere comportamento. Rode npm run build e npm test -- --watch=false ao final.
```

**Critério de aceite:**
- Build e testes verdes
- Nenhuma rota quebrada
- Diff < 500 linhas

### 4. Laboratório 2 — Refatoração guiada (`correcao_css.md`) via CLI (25 min)

**Problema:** validar responsividade do extrato em viewport 375px.

**Prompt sugerido:**
```
Com base em prompts/correcao_css.md, verifique se pix-history.component.css
atende mobile. Se não, aplique correção mínima usando apenas design tokens.
```

**Comparar:** mesmo prompt no Cursor vs Gemini CLI — tempo, qualidade do diff, necessidade de revisão humana.

### 5. Laboratório 3 — Testes do `PixReceiptComponent` (25 min)

**Problema:** comprovante não tem testes unitários.

**Prompt sugerido:**
```
Crie testes Vitest para PixReceiptComponent: renderiza valor formatado,
emite voltarInicio ao clicar no botão, exibe transactionId quando fornecido.
Use TestBed standalone. Não mockar o DOM inteiro.
```

**Critério de aceite:**
- ≥ 3 casos de teste novos
- `npm test -- --watch=false` verde

### 6. Encerramento (10 min)

- Checklist de aceite da aula (abaixo)
- Preview do **Exemplo 4** (Cypress + OpenSpec — testes E2E spec-driven)
- Tarefa de casa: exportar `briefing/extrato-figma.png` e abrir PR documentando diff

---

## Critérios de aceite da aula (Ex. 3)

- [ ] Gemini CLI (ou equivalente UNIPDS) configurado e executado no `pix-app`
- [ ] Código morto removido ou documentado com justificativa
- [ ] `npm run build` e `npm test` verdes após refatorações
- [ ] ≥ 1 refatoração feita **somente via CLI** (evidência: log ou screenshot do terminal)
- [ ] ≥ 3 testes novos em componente de UI (extrato ou comprovante)
- [ ] `docs/EVIDENCIAS_ACEITE.md` atualizado na pasta do Ex. 3 (ou Ex. 2 se trabalho in-place)

---

## Materiais de apoio

| Recurso | Caminho |
|---------|---------|
| App alvo | `modulo-5-exemplo-2-prototyping-ui/app/` |
| Prompts UNIPDS Ex. 2 | `modulo-5-exemplo-2-prototyping-ui/prompts/` |
| Aceite Ex. 2 | [`EVIDENCIAS_ACEITE.md`](EVIDENCIAS_ACEITE.md) |
| Revisão Angular MCP | [`MCP_REVISAO.md`](MCP_REVISAO.md) |
| UNIPDS modulo-03 | [GitHub](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-03) |

---

## Perguntas para discussão em sala

1. Quando usar **Cursor Agent** vs **CLI agent** no dia a dia?
2. Como evitar que o agente "reescreva o projeto inteiro"?
3. Qual o papel do humano no review de diffs gerados por IA?
4. Como os prompts do Ex. 1 e Ex. 2 reduzem retrabalho no Ex. 3?

---

## Tarefa para casa

1. ~~Criar `modulo-5-exemplo-3-openspec-cfp/`~~ ✅ feito pelo delivery-agent
2. Executar Laboratório 3 completo (testes do comprovante)
3. Registrar no [`EVIDENCIAS_ACEITE.md`](../../modulo-5-exemplo-3-openspec-cfp/docs/EVIDENCIAS_ACEITE.md)
