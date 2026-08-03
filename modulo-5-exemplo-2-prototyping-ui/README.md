# Prototyping UI — Figma to Code (Angular)

Este diretório é o **Módulo 5 — Exemplo 2** (`modulo-5-exemplo-2-prototyping-ui`) — adaptação local da pós UNIPDS.

Referência UNIPDS: [modulo-02](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-02)

## Objetivo

Transformar a especificação do **Exemplo 1** em **protótipo funcional** com **Angular 21**, cobrindo caminho feliz e unhappy paths do Pix Agendado.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| [Exemplo 1 concluído](../modulo-5-exemplo-1-discovery-refinement/) | Specs em `docs/refinement/` |
| Node.js 22+ | Angular CLI |
| Angular CLI 21 | `npx @angular/cli@21` |

Entrada detalhada: [`docs/ENTRADA_EXEMPLO_1.md`](docs/ENTRADA_EXEMPLO_1.md)

## Estrutura

```
modulo-5-exemplo-2-prototyping-ui/
├── .cursor/
│   └── mcp.json                      # Angular CLI MCP (local ao exemplo)
├── briefing/                         # UNIPDS — branding, figma-specs, stitch
│   ├── branding-briefing.txt
│   ├── figma-specs.txt
│   └── google-stitch.txt
├── prompts/
│   ├── README.md                     # Índice dos prompts (UNIPDS + locais)
│   ├── figma-to-angular.md           # UNIPDS — Figma → PixHistoryComponent
│   ├── componente-figma.txt            # UNIPDS — execução com imagem + specs
│   ├── design-tokens-generator.md      # UNIPDS — tokens CSS
│   ├── a11y-component-generator.md   # UNIPDS — componente acessível
│   ├── stitch-code-refactor.md       # UNIPDS — Stitch → Angular
│   ├── refatoracao-stich.txt           # UNIPDS — execução Stitch
│   ├── adicionar-fluxo-comprovante.txt # UNIPDS — integrar recibo
│   ├── criacao-menu-extrato.txt        # UNIPDS — rota /extrato
│   ├── correcao_css.md                 # UNIPDS — responsividade + a11y
│   ├── figma-to-code.md              # Local — Pix Agendado (Ex. 1 → app)
│   ├── google-stitch.md              # Local — Stitch → PixReceiptComponent
│   └── firebase-studio-prototyper.md # Trilha cloud UNIPDS (opcional)
├── docs/
│   ├── ENTRADA_EXEMPLO_1.md
│   ├── EVIDENCIAS_ACEITE.md        # Validação dos critérios ✅
│   ├── PROXIMA_AULA.md             # Roteiro Ex. 3 — Agents CLI
│   ├── MCP_REVISAO.md              # Alinhamento com get_best_practices (Angular MCP)
│   └── PIPELINE.md
└── app/                              # pix-app (Angular 21)
    ├── modelo/code.html              # HTML bruto Google Stitch
    ├── src/app/core/                 # models, messages, mock API, state
    ├── src/app/components/           # error-modal (a11y)
    ├── src/app/pix-transfer/         # wizard Pix Agendado
    ├── src/app/features/receipt/     # PixReceiptComponent (Stitch)
    ├── src/app/pix-history/          # extrato (/extrato)
    └── src/app/pix-schedules/        # agendamentos
```

## Como executar

### Criar o projeto (já feito)

```bash
cd modulo-5-exemplo-2-prototyping-ui
npx @angular/cli@21 new pix-app --directory app --style css --routing --skip-git --defaults --ssr=false
```

### Rodar localmente

```bash
cd app
npm start
```

Abra http://localhost:4200

| Rota | Tela |
|------|------|
| `/pix` | Wizard Pix Agendado + comprovante |
| `/extrato` | Extrato (`PixHistoryComponent`) |
| `/comprovante` | Preview comprovante Stitch |
| `/agendamentos` | Lista e cancelamento |

**Demo:** MFA senha `1234` · chave inválida `invalid@pix` · valor > saldo `3000`

### Angular MCP no Cursor

O servidor MCP do Angular CLI conecta o agente às ferramentas oficiais (`get_best_practices`, `find_examples`, etc.).

**Config local:** [`.cursor/mcp.json`](.cursor/mcp.json) (executa `npx @angular/cli mcp` na pasta `app/`).

**Config no repo raiz:** `.cursor/mcp.json` → servidor `angular-cli-pix-app` (quando o workspace é `pos-unipds-IA`).

1. Abra **Cursor Settings → MCP** e confira `angular-cli` ou `angular-cli-pix-app` ativo
2. Se não aparecer, recarregue a janela (`Developer: Reload Window`)
3. No chat, peça: *"use as best practices do Angular para criar um componente de revisão"*

Opções extras no `args` (opcional): `--read-only`, `-E modernize`, `-E devserver`

Referência: [Angular CLI MCP](https://angular.dev/ai/mcp)

Referência UNIPDS prompts: [pix-app/prompts](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-02/pix-app/prompts) · índice local em [`prompts/README.md`](prompts/README.md)

## Critérios de sucesso

- [x] Pasta no padrão `modulo-5-exemplo-2-*`
- [x] README local com objetivo e passo a passo
- [x] Entrada do Exemplo 1 documentada
- [x] App Angular 21 em `app/` (`npm run build` OK)
- [x] Caminho feliz Pix Agendado implementado
- [x] ≥ 3 unhappy paths (limite, saldo, cancelamento bloqueado, chave inválida)
- [x] Mensagens de `mensagens-ui.json` em `core/messages.ts`
- [x] Angular MCP configurado (`.cursor/mcp.json`)
- [x] Prompts UNIPDS em `prompts/` (9 arquivos oficiais + índice)
- [x] App revisado conforme `get_best_practices` ([`docs/MCP_REVISAO.md`](docs/MCP_REVISAO.md))
- [x] Critérios validados ([`docs/EVIDENCIAS_ACEITE.md`](docs/EVIDENCIAS_ACEITE.md))
- [x] Roteiro próxima aula ([`docs/PROXIMA_AULA.md`](docs/PROXIMA_AULA.md))
- [x] README raiz atualizado

## Mapeamento com Exemplo 1

| Spec Ex. 1 | Implementação Angular |
|------------|----------------------|
| `fluxo-logico.mmd` | Wizard em `pix-transfer/` + rotas `/pix`, `/agendamentos` |
| `mensagens-ui.json` | `core/messages.ts` |
| `ui-states-checklist.md` | Estados loading/empty/error + `ErrorModal` |
| `edge-cases.md` | Validações no wizard + mock API |
| Prompts UNIPDS extrato | `pix-history/` em `/extrato` |
| Prompts UNIPDS comprovante | `features/receipt/` integrado em `pix-transfer` + `/comprovante` |

## Próximo passo

**Exemplo 3 criado:** [`modulo-5-exemplo-3-agents-cli`](../modulo-5-exemplo-3-agents-cli/) — Agents CLI (scaffold via delivery-agent).

Roteiro: [`docs/PROXIMA_AULA.md`](docs/PROXIMA_AULA.md) · Relatório didático: [`../modulo-5-exemplo-3-agents-cli/docs/RELATORIO_DIDATICO.md`](../modulo-5-exemplo-3-agents-cli/docs/RELATORIO_DIDATICO.md)

## Exemplo anterior

[`modulo-5-exemplo-1-discovery-refinement`](../modulo-5-exemplo-1-discovery-refinement/) ✅
