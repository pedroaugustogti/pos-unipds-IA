# Testes

| Arquivo | O que valida |
|---------|----------------|
| `test/tools/csvToJSONTool.test.ts` | Tool local `csv_to_json` (sem rede). |
| `test/e2e/http.e2e.test.ts` | Fastify `POST /chat` — schema (400). |
| `test/e2e/chat.pipeline.e2e.test.ts` | Pipeline completo. Só roda com `npm run test:e2e:full` (define `RUN_FULL_E2E=1`). |

## Comandos

```bash
npm test
```

E2E completo (OpenRouter + intent estruturado + agente com MCP). Timeout por teste **90s** (`npm run test:e2e:full` usa `--test-timeout=100000`). Pode falhar com modelos free se o JSON do intent não bater no schema; use modelo pago ou rode com Mongo (`docker compose up -d`). Os servidores MCP estão em `dependencies` e são fechados no `after` do e2e (`closeMcpConnections`).

```bash
npm run test:e2e:full
```
