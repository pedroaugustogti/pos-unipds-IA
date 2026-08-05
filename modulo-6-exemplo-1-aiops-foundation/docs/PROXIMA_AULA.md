# Próxima Aula — Exemplo 2: IaC Copilot + Terraform

> **Scaffold previsto:** `modulo-6-exemplo-2-iac-copilot` (Lab 2 do monorepo Nexus)

**Referência UNIPDS:** [modulo06-aiops-engenharia-agentica/labs/modulo2_iac_copilot.py](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/blob/main/modulo06-aiops-engenharia-agentica/labs/modulo2_iac_copilot.py)

---

## Contexto pedagógico

| Aula anterior | Esta aula | Próxima |
|---------------|-----------|---------|
| Ex. 1 — Foundation ✅ | **Ex. 2 — IaC Copilot** | Ex. 3 — K8s GitOps |

**Ponte com o Ex. 1:** na Foundation o agente **consulta** políticas. No IaC Copilot ele **gera código Terraform HCL** e passa por auditoria DevSecOps.

---

## Objetivos

1. Executar `labs/modulo2_iac_copilot.py`
2. Gerar `main.tf` aderente às normas Nexus
3. Entender o agente `get_auditor` e validação de compliance
4. Comparar output HCL antes/depois da auditoria

---

## Pré-requisitos

- Ex. 1 concluído (venv, Groq, familiaridade com CrewAI)
- Terraform CLI (opcional — para validar HCL gerado)

---

## Início rápido

```powershell
cd ../modulo-6-exemplo-1-aiops-foundation/nexus
.\venv\Scripts\Activate.ps1
python labs/modulo2_iac_copilot.py
```

---

## Materiais

| Documento | Conteúdo |
|-----------|----------|
| [`nexus/slides/slides2.md`](../nexus/slides/slides2.md) | Slides UNIPDS Lab 2 |
| [`nexus/main.tf`](../nexus/main.tf) | Exemplo de HCL gerado |
| [`FLUXO_CREWAI.md`](FLUXO_CREWAI.md) | Arquitetura agentes + tools |

---

## Comandos de validação

```powershell
python labs/modulo2_iac_copilot.py
# Verificar se main.tf foi gerado/atualizado com prefixo nexus- e região us-east-1
```
