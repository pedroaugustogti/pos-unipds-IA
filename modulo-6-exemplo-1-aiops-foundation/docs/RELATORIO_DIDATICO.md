# Relatório Didático — Exemplo 1: Nexus AI-Ops Foundation

> Scaffold via delivery-agent · material base [UNIPDS modulo06-aiops-engenharia-agentica](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo06-aiops-engenharia-agentica)

## Posição no curso

O Exemplo 1 **abre o Módulo 6** com IA aplicada a **operações de plataforma**. Enquanto o Módulo 5 embutiu IA no produto final (BragBot + Genkit), o Nexus coloca agentes no loop de **infraestrutura, compliance e incidentes**.

## Competências trabalhadas

| Competência | Como aparece na aula |
|-------------|---------------------|
| AI-Ops consultivo | Agente que projeta recursos seguindo políticas |
| Engenharia agêntica | CrewAI: Agent + Task + Tool + Crew |
| Governança | Policy RAG via `check_compliance_rules` |
| LLM em produção | Groq Llama 3.1 com temperatura baixa (0.2) |
| Trilha progressiva | 12 labs do Foundation ao projeto final |

## Stack técnica

- **Python 3.11** + venv
- **CrewAI** + `crewai[tools]`
- **Groq** (`langchain-groq`) — `llama-3.1-8b-instant`
- **python-dotenv** para secrets
- Monorepo UNIPDS com labs, tools, core, ui, k8s

## Ponte pedagógica

```
Módulo 5 Ex. 6: IA no PRODUTO (Genkit + Angular)
Módulo 6 Ex. 1: IA na PLATAFORMA (CrewAI + compliance)
Módulo 6 Ex. 2+: IaC, K8s, troubleshooting, orquestração
```

## Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| API key exposta | `.env` no `.gitignore`, `.env.example` no repo |
| Python 3.14 incompatível | Documentar 3.10–3.13 |
| Custo Groq | Modelo 8B instant, demos curtas em sala |
| Confusão Módulo 5 vs 6 | Tabela comparativa em `FLUXO_CREWAI.md` |

## Entregáveis do aluno

1. Lab 1 executado com saída capturada
2. Evidências em [`EVIDENCIAS_ACEITE.md`](EVIDENCIAS_ACEITE.md)
3. (Opcional) Task customizada em `modulo1_foundation.py`
