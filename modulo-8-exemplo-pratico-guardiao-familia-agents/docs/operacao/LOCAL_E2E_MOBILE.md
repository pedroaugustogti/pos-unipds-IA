# Ambiente local E2E mobile — Guardião Família

Stack para agentes **frontend-mobile** e **qa** validarem pareamento e fluxos Android de ponta a ponta.

## Pré-requisitos (Windows)

| Componente | Versão / nota |
|------------|----------------|
| Docker Desktop | Postgres + Redis + API (`docker-compose.dev.yml`) |
| Node.js + npm | Repos `api`, `parent`, `child` |
| Android Studio | SDK Platform 34+, emulador Pixel 6 |
| `ANDROID_HOME` | Ex.: `%LOCALAPPDATA%\Android\Sdk` |
| AVDs | `Pixel_6_API_34` (5554) e opcional segundo (5556) |
| Dev clients | `expo run:android` em parent e child (uma vez) |
| Appium 2 | `npm run appium:doctor` no repo API |

## Portas

| Serviço | Host | Emulador (`10.0.2.2`) |
|---------|------|------------------------|
| API | `127.0.0.1:3000` | `:3000` |
| Postgres | `127.0.0.1:5432` | — |
| Metro parent | `8082` | `8082` |
| Metro child | `9090` | `9090` |
| Appium | `4723` | — |

> Parent usa porta **8082** no E2E (Appium). Child: `9090`. API no emulador: `http://10.0.2.2:3000/api/v1`.

## Subir stack (automático)

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
powershell -ExecutionPolicy Bypass -File .\agents\qa-gate\scripts\local_e2e_stack.ps1 -Mode ApiOnly
```

Modos:

- `Check` — pré-requisitos
- `ApiOnly` — Docker + migrations + seed + smoke API pareamento
- `Full` — acima + emuladores + Metro + Appium pairing

CLI Python (agentes):

```bash
python agents/01-role-based/qa-gate/scripts/local_e2e_smoke.py check
python agents/01-role-based/qa-gate/scripts/local_e2e_smoke.py up
python agents/01-role-based/qa-gate/scripts/local_e2e_smoke.py pairing-api --json
python agents/01-role-based/qa-gate/scripts/local_e2e_smoke.py full
```

## Fluxo manual (referência)

1. **API:** `guardiao-familia-api` → `docker compose -f docker-compose.dev.yml up -d --build`
2. **Migrations:** `set DATABASE_URL=postgresql://guardiao_admin:password@127.0.0.1:5432/guardiao_familia` → `npm run migration:run` → `npm run seed`
3. **Emuladores:** `npm run emulators:start` (API repo)
4. **Metro parent:** `npx expo start --port 8082` + `EXPO_PUBLIC_API_BASE_URL=http://10.0.2.2:3000/api/v1`
5. **Metro child:** `npm start` (porta 9090) + `EXPO_PUBLIC_API_BASE_URL_EMULATOR=http://10.0.2.2:3000/api/v1`
6. **Appium:** `npm run test:appium:pairing:android:dual`

## Evidências QA

- **Mobile (canônico):** `guardiao-familia-mobile-setup` via `python agents/01-role-based/qa-gate/scripts/qa_mobile_evidence.py` — ver `agents/01-role-based/qa-gate/MOBILE_SETUP_EVIDENCE.md`
- **API:** report JSON em stdout (`task36-prototipo-v2`)
- Agentes publicam comentário na issue via `lib/qa_mobile.format_qa_mobile_comment` ou `format_evidence_comment`

## Credenciais dev (seed)

- Email: `admin@guardiao.local`
- Senha: `GuardiaoDev2026!`

## Troubleshooting

- **Docker pipe error:** iniciar Docker Desktop e aguardar ~2 min
- **`.env` ausente:** script copia de `.env.example` automaticamente
- **Build API Docker falha (TLS Alpine):** script usa fallback Postgres+Redis no Docker e API no host (`npm run start:dev`)
- **npm `UNABLE_TO_VERIFY_LEAF_SIGNATURE`:** proxy/cert corporativo — instale CA raiz ou `npm config set strict-ssl false` (somente dev) e rode `npm ci` no repo API
- **adb não encontrado:** definir `ANDROID_HOME` e reiniciar terminal; instalar Android Studio + AVD Pixel API 34
- **Metro 8082 vs 8081:** E2E usa 8082; não usar `npm start` default do parent sem ajustar URL do dev client
