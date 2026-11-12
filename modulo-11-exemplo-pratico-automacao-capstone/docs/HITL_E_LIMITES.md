# HITL e limites — o que não automatizar

Mesmo com MCP e Playwright, o Capstone mantém **humano no circuito** onde há dinheiro, identidade ou ato irreversível.

## Sempre HITL (nível C)

| Ação | Por quê |
|------|---------|
| Criar/ligar **faturamento** GCP | Cartão / spending |
| Criar **Cloud SQL** (primeira vez) | Custo contínuo + ~20–30 min |
| Criar **Workload Identity** / IAM amplo | Superfície de ataque |
| Apagar projeto / teardown produção | Irreversível / perda de dados |
| Commitar secrets / JSON de service account | Vazamento |
| Publicar recomendação de investimento | Regra de negócio + CVM |

## HITL na primeira vez, depois A/B

| Ação | Depois pode |
|------|-------------|
| API keys Langfuse / Serper / Vertex | Rotacionar via Secret Manager com review |
| Firebase project link | Redeploy Hosting via Actions |
| Aceitar OAuth GitHub MCP | Reusar token |

## Playwright no Console GCP — cuidados

- Seletores mudam; use só para **assistir** (preencher form, tirar evidência), não como única fonte de verdade.
- Preferir **gcloud** / Google MCP para create/describe.
- Nunca gravar senha no script Playwright versionado.

## MCP — cuidados

- GitHub MCP: escopo mínimo (repos do Capstone).
- SQL MCP: preferir usuário read-only em produção.
- Capstone MCP (U3): tools de leitura/consulta primeiro; escrita com gate.
- Langfuse MCP: keys só em env local / Secret Manager.

## Analogia Guardião

No Guardião, merge/wipe/deploy param em `hitl_guard_actuation`.  
No Capstone, o equivalente é: **billing, IAM, teardown e recomendação financeira**.
