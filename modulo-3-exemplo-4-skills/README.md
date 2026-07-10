# Skills para Cursor — Módulo 3 Exemplo 4

Exemplo do **Módulo 3** demonstrando como instalar **Agent Skills** no Cursor via [skills.sh](https://www.skills.sh/), habilitando capacidades de navegação em browser e processamento de mídia com FFmpeg.

## Skills instaladas

| Skill | Fonte | Installs | Uso |
|-------|-------|----------|-----|
| [agent-browser](https://www.skills.sh/vercel-labs/agent-browser/agent-browser) | vercel-labs/agent-browser | 532K+ | Navegação, formulários, screenshots, QA |
| [ffmpeg](https://skills.sh/digitalsamba/claude-code-video-toolkit/ffmpeg) | digitalsamba/claude-code-video-toolkit | 5K+ | Conversão, compressão, áudio, Remotion |
| [ffmpeg-video-editor](https://skills.sh/sundial-org/awesome-openclaw-skills/ffmpeg-video-editor) | sundial-org/awesome-openclaw-skills | 1.3K+ | Edição por linguagem natural (cortar, converter, GIF) |

## Estrutura

```
modulo-3-exemplo-4-skills/
├── .agents/skills/          # instaladas via skills CLI
│   ├── agent-browser/
│   ├── ffmpeg/
│   └── ffmpeg-video-editor/
├── .cursor/skills/          # cópias para descoberta nativa do Cursor
├── skills-lock.json         # lockfile das skills instaladas
├── package.json
└── README.md
```

## Instalação

```bash
cd modulo-3-exemplo-4-skills
npm install
npm run browser:install   # Chromium para agent-browser
```

### Reinstalar todas as skills

```bash
npm run skills:install
```

Ou individualmente:

```bash
npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser -y
npx skills add https://github.com/digitalsamba/claude-code-video-toolkit --skill ffmpeg -y
npx skills add https://github.com/sundial-org/awesome-openclaw-skills --skill ffmpeg-video-editor -y
```

### Pré-requisito FFmpeg

As skills de FFmpeg assumem `ffmpeg` e `ffprobe` no PATH do sistema:

- Windows: [ffmpeg.org/download](https://ffmpeg.org/download.html) ou `winget install Gyan.FFmpeg`
- macOS: `brew install ffmpeg`

## Como usar no Cursor

1. Abra o workspace em `modulo-3-exemplo-4-skills`
2. O Cursor carrega skills de `.cursor/skills/` e `.agents/skills/`
3. Exemplos de prompts:

**Browser:**
> Use agent-browser para abrir https://example.com e tirar um screenshot

**FFmpeg (produção):**
> Use a skill ffmpeg para converter este GIF em MP4 compatível com web

**FFmpeg (edição):**
> Use ffmpeg-video-editor para cortar video.mp4 de 1:21 até 1:35

## Scripts npm

| Script | Descrição |
|--------|-----------|
| `npm run browser:install` | Instala Chromium para agent-browser |
| `npm run browser:skills` | Lista skills da CLI agent-browser |
| `npm run browser:core` | Carrega workflow principal do agent-browser |
| `npm run skills:install` | Reinstala todas as skills do exemplo |

## Referências

- [skills.sh — diretório de skills](https://www.skills.sh/)
- [agent-browser](https://github.com/vercel-labs/agent-browser)
- [claude-code-video-toolkit / ffmpeg](https://github.com/digitalsamba/claude-code-video-toolkit)
- [awesome-openclaw-skills / ffmpeg-video-editor](https://github.com/sundial-org/awesome-openclaw-skills)
