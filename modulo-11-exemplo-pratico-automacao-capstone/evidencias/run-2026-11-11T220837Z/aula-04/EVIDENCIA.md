# Evidência — Aula 4: GitHub e GitHub Actions / WIF

- **Status:** `executado`
- **Ferramenta (vídeo-aula):** GitHub Actions + WIF
- **Timestamp UTC:** 2026-11-11T220837Z

## Checks

| Check | OK | Detalhe |
|-------|----|---------|
| deploy.yml | ✅ | workflow presente |
| WIF no workflow | ✅ | google-github-actions/auth |
| id-token: write | ✅ | permissions OIDC |
| jobs test+deploy | ✅ | test → deploy |

## Notas

Workflow inspecionado; binding IAM GCP permanece HITL.
