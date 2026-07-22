# Atividade: servidor MCP de criptografia do zero

Este diretório é o **Módulo 3 — Exemplo 5** (`modulo-3-exemplo-5-server-mcp`) e serve como **material de apoio** para a atividade da pós-graduação sobre **criação de servidores MCP (Model Context Protocol)**.

## Objetivo da atividade (Pós)

A entrega esperada **não é** apenas rodar `encrypt`/`decrypt` no Node.js manualmente. O foco é demonstrar que você consegue:

1. Entender a arquitetura de um **servidor MCP** (transporte, tools, resources, prompts)
2. **Subir o servidor localmente** e conectá-lo ao Cursor/VS Code
3. Usar as **tools** `encrypt_message` e `decrypt_message` via agente
4. Validar o comportamento com **testes automatizados**

O código base veio do repositório oficial da disciplina:

- [05-mcps-do-zero-z](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo03-mcp-na-pratica/05-mcps-do-zero-z)

## O que há nesta pasta

| Arquivo / pasta | Papel |
|-----------------|--------|
| `src/index.ts` | Ponto de entrada — conecta o servidor ao transporte **stdio** |
| `src/mcp.ts` | Registro das **tools**, **resources** e **prompts** MCP |
| `src/service.ts` | Lógica de criptografia AES-256-CBC (camada de domínio) |
| `tests/` | Testes de integração que sobem o servidor real via stdio |
| `.vscode/mcp.json` | Configuração para o Cursor/VS Code usar o servidor |
| `package.json` | Scripts (`start`, `test`, `mcp:inspect`) e dependências |
| `refs.txt` | Links de referência (MCP Inspector, documentação) |

### Capacidades expostas pelo servidor

| Tipo | Nome | Descrição |
|------|------|-----------|
| Tool | `encrypt_message` | Criptografa texto com uma passphrase |
| Tool | `decrypt_message` | Descriptografa um texto previamente criptografado |
| Resource | `encryption://info` | Documenta algoritmo, derivação de chave e formato de saída |
| Prompt | `encrypt_message_prompt` | Template pronto para pedir criptografia ao agente |

> **Importante:** o servidor roda em **stdio** (entrada/saída padrão). Por isso os logs vão para `stderr` — o `stdout` é reservado ao protocolo MCP.

## Como realizar a atividade (passo a passo)

### 1. Pré-requisitos

- **Node.js v24+** (`node -v`)
- Dependências instaladas:

```bash
cd modulo-3-exemplo-5-server-mcp
npm install
```

> Em redes corporativas com proxy/SSL, pode ser necessário:
> `set NODE_OPTIONS=--use-system-ca` (Windows) antes do `npm install`.

### 2. Rodar os testes

```bash
npm test
```

Resultado esperado: **4 testes passando** (encrypt, decrypt round-trip, resource, prompt).

### 3. Conectar o servidor ao Cursor

O arquivo `.vscode/mcp.json` já está configurado:

```json
{
  "servers": {
    "ciphersuite-mcp": {
      "command": "node",
      "args": ["--experimental-strip-types", "src/index.ts"]
    }
  }
}
```

1. Abra o workspace em `modulo-3-exemplo-5-server-mcp` (ou na raiz do monorepo)
2. Recarregue a janela: **Developer: Reload Window**
3. Confirme que o servidor `ciphersuite-mcp` aparece nas configurações MCP do Cursor

### 4. Testar via agente (chat)

Envie prompts como:

> Criptografe a mensagem "Olá, pós UNIPDS!" usando a passphrase "minha-chave-secreta" com a tool `encrypt_message`.

> Descriptografe o ciphertext `<cole_aqui_o_resultado>` com a passphrase "minha-chave-secreta".

> Leia o resource `encryption://info` e me explique o algoritmo usado.

### 5. (Opcional) Explorar com o MCP Inspector

Interface visual para testar tools sem o agente:

```bash
npm run mcp:inspect
```

Abre em `http://localhost:5173` — veja também [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector).

### Critérios de sucesso

- [ ] `npm test` passa com **4/4** testes
- [ ] O servidor MCP aparece conectado no Cursor
- [ ] `encrypt_message` retorna texto no formato `iv_hex:ciphertext_hex`
- [ ] `decrypt_message` recupera o texto original com a **mesma passphrase**
- [ ] Passphrase incorreta retorna erro (`isError: true`), sem derrubar o servidor
- [ ] O agente consegue ler o resource `encryption://info`

## Referência técnica

### Como a criptografia funciona

| Aspecto | Detalhe |
|---------|---------|
| Algoritmo | **AES-256-CBC** |
| Derivação de chave | `scrypt(passphrase, saltFixo, 32)` → chave de 256 bits |
| IV | 16 bytes aleatórios por operação (`randomBytes`) |
| Formato de saída | `<iv_em_hex>:<ciphertext_em_hex>` |
| Encoding | UTF-8 |

O mesmo texto criptografado duas vezes produz **saídas diferentes** (IV aleatório). Para descriptografar, use a **mesma passphrase** e o **ciphertext completo** (incluindo o IV).

### Arquitetura do projeto

```
Cliente MCP (Cursor / Inspector / Testes)
        ↓  stdio (JSON-RPC)
   src/index.ts          ← transporte
        ↓
   src/mcp.ts            ← protocolo (tools, resources, prompts)
        ↓
   src/service.ts        ← criptografia (node:crypto)
```

### Trecho central — camada de serviço (`service.ts`)

```typescript
const SALT = 'mcp-encrypter-salt';

function deriveKey(passphrase: string): Buffer {
    return scryptSync(passphrase, SALT, 32);
}

export function encrypt(text: string, key: string): string {
    const iv = randomBytes(16);
    const cipher = createCipheriv('aes-256-cbc', deriveKey(key), iv);
    const encrypted = Buffer.concat([
        cipher.update(Buffer.from(text, 'utf8')),
        cipher.final(),
    ]);
    return `${iv.toString('hex')}:${encrypted.toString('hex')}`;
}
```

A função `decrypt` faz o caminho inverso: separa `iv:ciphertext`, deriva a chave com `scrypt` e usa `createDecipheriv`.

### Trecho central — registro de tool MCP (`mcp.ts`)

```typescript
server.registerTool('encrypt_message', {
    description: 'Encrypt a message',
    inputSchema: {
        message: z.string(),
        encryptionKey: z.string(),
    },
    outputSchema: {
        encryptedMessage: z.string(),
    },
}, async ({ message, encryptionKey }) => {
    const encryptedMessage = encrypt(message, encryptionKey);
    return {
        content: [{ type: "text", text: encryptedMessage }],
        structuredContent: { encryptedMessage },
    };
});
```

Cada tool retorna:
- **`content`** — texto legível para o agente
- **`structuredContent`** — dados tipados (usados nos testes)

Erros são capturados com `try/catch` e retornam `isError: true` em vez de encerrar o processo.

### Como os testes validam o servidor

Os testes em `tests/helpers.ts` sobem o servidor **de verdade** via stdio:

```typescript
const transport = new StdioClientTransport({
    command: 'node',
    args: ['--experimental-strip-types', 'src/index.ts'],
});
const client = new Client({ name: 'test-client', version: '1.0.1' }, { capabilities: {} });
await client.connect(transport);
```

Isso garante que o protocolo MCP inteiro funciona — não apenas as funções `encrypt`/`decrypt` isoladas.

## Fluxo da atividade (MCP)

```
Você (prompt no Cursor)
        ↓
Agente descobre tools do servidor ciphersuite-mcp
        ↓
encrypt_message("texto", "passphrase")
        ↓
Retorna "a3f1...:bfca27..."  (iv:ciphertext)
        ↓
decrypt_message("a3f1...:bfca27...", "passphrase")
        ↓
Retorna "texto" original
```

## Scripts disponíveis

| Script | Descrição |
|--------|-----------|
| `npm start` | Inicia o servidor MCP (stdio) |
| `npm run dev` | Inicia com watch e inspector do Node |
| `npm test` | Roda a suíte de testes |
| `npm run test:dev` | Testes em modo watch |
| `npm run mcp:inspect` | Abre o MCP Inspector no browser |

## Relação com o Módulo 3

Este exemplo integra a trilha **MCP na prática** do Módulo 3:

| Exemplo | Tema |
|---------|------|
| Exemplo 1 | Agente LangGraph consumindo **tools MCP externas** |
| Exemplo 2 | Agente com Google Trends + MCP |
| Exemplo 3 | Dev instructions e agents customizados |
| Exemplo 4 | **Skills** (ffmpeg, agent-browser) |
| **Exemplo 5** | **Criar um servidor MCP do zero** ← este projeto |

O aprendizado central é: **MCP padroniza como agentes descobrem e executam capacidades externas** — tools, resources e prompts — sem acoplar o agente à implementação interna do serviço.

## Observações para estudo

- O salt em `service.ts` é **fixo** — adequado para exemplo didático; em produção, use salt por usuário e parâmetros de custo explícitos no `scrypt`.
- O servidor não persiste dados: cada chamada é stateless.
- Não há etapa de build: TypeScript roda nativamente com `node --experimental-strip-types` (Node 24+).
