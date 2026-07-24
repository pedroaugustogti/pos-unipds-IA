# Atividade: Agent Skills no Cursor

Este diretório é o **Módulo 3 — Exemplo 4** (`modulo-3-exemplo-4-skills`) e serve como **material de apoio** para a atividade da pós-graduação sobre **utilização de Agent Skills**.

## Objetivo da atividade (Pós)

A entrega esperada **não é** executar FFmpeg ou Playwright manualmente no terminal. O foco é demonstrar que o **agente do Cursor**, guiado pelas **skills instaladas no projeto**, consegue:

1. Carregar skills de `.cursor/skills/` automaticamente
2. Resolver tarefas especializadas (browser, vídeo) a partir de linguagem natural
3. Montar e executar comandos corretos (FFmpeg, agent-browser) sem repetir instruções em todo prompt

Skills instaladas via [skills.sh](https://www.skills.sh/):

| Skill | Uso principal |
|-------|----------------|
| [agent-browser](https://www.skills.sh/vercel-labs/agent-browser/agent-browser) | Navegação, formulários, screenshots, QA |
| [ffmpeg](https://www.skills.sh/digitalsamba/claude-code-video-toolkit/ffmpeg) | Conversão e compressão de mídia |
| [ffmpeg-video-editor](https://www.skills.sh/sundial-org/awesome-openclaw-skills/ffmpeg-video-editor) | Edição por linguagem natural |

## Atividade prática principal

A subpasta **[`sample-video-ffmpeg/`](./sample-video-ffmpeg/)** contém o exercício guiado de conversão de vídeo para preto e branco. **Leia o README completo dessa pasta** antes de entregar a atividade.

## O que há nesta pasta

| Item | Papel |
|------|--------|
| `.cursor/skills/` | Skills descobertas pelo Cursor |
| `.agents/skills/` | Instalação via CLI `skills` |
| `skills-lock.json` | Lockfile das versões instaladas |
| `sample-video-ffmpeg/` | **Atividade prática** — conversão de vídeo com skill FFmpeg |
| `package.json` | Scripts de instalação |

## Como realizar a atividade (passo a passo)

### 1. Instalar dependências e skills

```bash
cd modulo-3-exemplo-4-skills
npm install
npm run skills:install
npm run browser:install   # Chromium para agent-browser
```

### 2. Instalar FFmpeg no sistema

- Windows: [ffmpeg.org/download](https://ffmpeg.org/download.html) ou `winget install Gyan.FFmpeg`
- Confirme: `ffmpeg -version`

### 3. Realizar a atividade de vídeo

Siga o guia em [`sample-video-ffmpeg/README.md`](./sample-video-ffmpeg/README.md).

### 4. (Opcional) Testar outras skills

**Browser:**
> Use agent-browser para abrir https://example.com e tirar um screenshot

**FFmpeg:**
> Use a skill ffmpeg para converter um vídeo para formato web

### Critérios de sucesso

- [ ] Skills visíveis em `.cursor/skills/`
- [ ] Atividade de vídeo feita **via agente** (não manualmente), conforme `sample-video-ffmpeg/`
- [ ] Agente referenciou a skill `ffmpeg` ou `ffmpeg-video-editor`
- [ ] (Opcional) agent-browser executou navegação ou screenshot com sucesso

## Fluxo da atividade (skills)

```
Você (prompt no Cursor)
        ↓
Agente carrega skill (ffmpeg / agent-browser / …)
        ↓
Agente monta comando ou fluxo especializado
        ↓
Resultado (arquivo, screenshot, etc.)
```

## Scripts npm

| Script | Descrição |
|--------|-----------|
| `npm run skills:install` | Reinstala todas as skills |
| `npm run browser:install` | Instala Chromium |
| `npm run browser:skills` | Lista skills do agent-browser |

## Relação com o Módulo 3

| Exemplo | Tema |
|---------|------|
| Exemplo 1–3 | Agentes + MCP / dev instructions |
| **Exemplo 4** | **Skills** — conhecimento reutilizável no agente ← este projeto |
| Exemplo 5–7 | Servidores MCP e integração com APIs |

O aprendizado central é: **skills estendem o agente** com conhecimento e fluxos especializados, complementando MCP (ferramentas) e prompts ad hoc.

## Referências

- [skills.sh](https://www.skills.sh/)
- [agent-browser](https://github.com/vercel-labs/agent-browser)
