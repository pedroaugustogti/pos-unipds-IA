# Atividade: conversão de vídeo com Skills no Cursor

Este diretório faz parte do **Módulo 3 — Exemplo 4** (`modulo-3-exemplo-4-skills`) e serve como **material de apoio** para a atividade da pós-graduação sobre **utilização de Agent Skills**.

## Objetivo da atividade (Pós)

A entrega esperada **não é** rodar FFmpeg manualmente no terminal. O foco é demonstrar que o **agente do Cursor**, guiado pelas **skills instaladas no projeto**, consegue:

1. Entender um pedido em linguagem natural (ex.: “converter este vídeo para preto e branco”)
2. Carregar a skill adequada (`ffmpeg` ou `ffmpeg-video-editor`)
3. Montar e executar o comando FFmpeg correto
4. Gerar o arquivo de saída na pasta `sample-video-ffmpeg/`

As skills ficam em:

- `.cursor/skills/ffmpeg/`
- `.cursor/skills/ffmpeg-video-editor/`

Instaladas via [skills.sh](https://www.skills.sh/) — veja o `README.md` na raiz do módulo.

## O que há nesta pasta

| Arquivo | Papel |
|---------|--------|
| `sample-original.mp4` | Vídeo colorido de entrada (material para você usar na atividade) |
| `sample-black-and-white.mp4` | **Referência** do resultado esperado (gerado previamente para comparação) |
| `README.md` | Este guia |

> **Importante:** o arquivo `sample-black-and-white.mp4` existe como **exemplo de saída**, para você validar se o agente produziu algo equivalente. Na atividade da pós, **você deve pedir ao Cursor para fazer a conversão usando a skill**, não copiar o comando deste README sem passar pelo agente.

## Como realizar a atividade (passo a passo)

1. Abra o workspace em `modulo-3-exemplo-4-skills` no Cursor
2. Confirme que as skills estão em `.cursor/skills/` (ou reinstale com `npm run skills:install`)
3. Instale o FFmpeg no sistema, se ainda não tiver (`ffmpeg -version`)
4. No chat do **Agent**, envie um prompt como:

   > Use a skill **ffmpeg** (ou **ffmpeg-video-editor**) para converter o vídeo `sample-video-ffmpeg/sample-original.mp4` em preto e branco e salvar como `sample-video-ffmpeg/sample-black-and-white-sua-versao.mp4`

5. Observe o agente:
   - carregar a skill
   - propor o comando FFmpeg
   - executar via terminal
6. Compare o resultado com `sample-black-and-white.mp4` (referência)

### Critérios de sucesso

- [ ] O pedido foi feito **ao agente do Cursor**, não executado manualmente por você
- [ ] O agente **referenciou ou aplicou** a skill `ffmpeg` ou `ffmpeg-video-editor`
- [ ] O vídeo de saída está em escala de cinza (preto e branco)
- [ ] O áudio foi preservado (se aplicável)

## Referência técnica (resultado esperado)

A conversão de referência usa o filtro `hue=s=0`, que zera a saturação. O agente, guiado pela skill, pode chegar ao mesmo resultado com filtros equivalentes (`format=gray`, `eq=saturation=0`, etc.).

```bash
ffmpeg -y -hide_banner \
  -i "sample-original.mp4" \
  -vf "hue=s=0" \
  -c:a copy \
  "sample-black-and-white.mp4"
```

| Parâmetro | Função |
|-----------|--------|
| `-y` | Sobrescreve o arquivo de saída |
| `-hide_banner` | Oculta banner do FFmpeg |
| `-i` | Arquivo de entrada |
| `-vf "hue=s=0"` | Remove saturação (preto e branco) |
| `-c:a copy` | Copia áudio sem reencodar |

### Verificar o resultado

```bash
ffprobe -v quiet -print_format json -show_format -show_streams sample-black-and-white.mp4
```

## Fluxo da atividade (skills)

```
Você (prompt no Cursor)
        ↓
Agente carrega skill ffmpeg / ffmpeg-video-editor
        ↓
Agente monta comando FFmpeg
        ↓
sample-original.mp4  →  conversão  →  seu-arquivo-saida.mp4
```

## Origem do vídeo de exemplo

O `sample-original.mp4` foi obtido de uma fonte pública:

- URL: `https://download.samplelib.com/mp4/sample-5s.mp4`
- Formato: MP4, ~5s, 1920×1080, H.264 + AAC

## Relação com o módulo

Este exemplo integra o **Exemplo 4 — Skills** do Módulo 3, junto com:

- **agent-browser** — automação de navegador
- **ffmpeg** — processamento de mídia para produção
- **ffmpeg-video-editor** — edição por linguagem natural

O aprendizado central é: **skills estendem o agente** com conhecimento e fluxos especializados, sem precisar repetir instruções em todo prompt.

## Relação com a publicação de MCP (Exemplo 8)

No [`modulo-3-exemplo-8-publish-mcp`](../modulo-3-exemplo-8-publish-mcp/), o servidor MCP dos exemplos 6 e 7 é empacotado e publicado no npm para consumo via `npx` e no Cursor:

```
Servidor MCP (código dos ex. 6/7)
        ↓
Empacotamento npm (bin, files, tsx no bin)
        ↓
Verdaccio local (:4873) — registry privado
        ↓
npmjs.org — @gorgan/customers-mcp
        ↓
npm publish + validação e2e (CRUD)
        ↓
Cursor — customers-mcp-public (5 tools)
```

| Etapa | Comando / artefato |
|-------|-------------------|
| Registry privado | `npm run release:private` |
| Registry público | `npm run release:public` |
| Validação | `npm run validate:e2e` |
| Cursor | `scripts/start-public-mcp.mjs` |

### Pacotes publicados neste workspace

| Registry | Pacote | Uso |
|----------|--------|-----|
| Verdaccio (`localhost:4873`) | `@pedroaugusto/customers-mcp` | Registry privado local (usuário `pedroaugusto`) |
| npm público | [`@gorgan/customers-mcp`](https://www.npmjs.com/package/@gorgan/customers-mcp) | Consumo via `npx` e MCP `customers-mcp-public` no Cursor |

### Critérios de sucesso (publicação MCP)

- [ ] Pacote publicado no Verdaccio e/ou npm público
- [ ] `npm run validate:e2e` passa (API legada + CRUD via `npx`)
- [ ] `customers-mcp-public` conectado no Cursor com 5 tools
- [ ] Agente consegue chamar `list_customers` / `create_customer` na API legada

Guia completo: [`modulo-3-exemplo-8-publish-mcp/README.md`](../modulo-3-exemplo-8-publish-mcp/README.md).
