# Relatório — OKRs (Objectives and Key Results)

> **Módulo 7 UNIPDS — Ferramentas de IA para Gestão de Projetos**
> Caso **RouteWise** · PM AI Toolkit (Prof. Ahirton Lopes)
> Submódulo **M10 — Portfolio e OKRs**

**Relatório completo M10:** [`RELATORIO_M10_PORTFOLIO_OKRS_IA.md`](./RELATORIO_M10_PORTFOLIO_OKRS_IA.md)

**Referência cruzada:** [`RELATORIO_RICE_VS_WSJF.md`](./RELATORIO_RICE_VS_WSJF.md) (seção 10 — OKRs derivados do discovery)

---

## 1. Definição

**OKR** = **Objectives and Key Results** — **Objetivos e Resultados-Chave**.

Framework de gestão estratégica que conecta **o que se quer alcançar** (qualitativo) com **como se mede o progresso** (quantitativo).

| Componente | Pergunta | Característica |
|------------|----------|----------------|
| **O — Objective** | O que queremos alcançar? | Direcional, inspirador, memorável |
| **KR — Key Result** | Como sabemos que chegamos lá? | Mensurável, prazo, baseline |

---

## 2. Diferença vs RICE/WSJF

| Framework | Pergunta | Momento |
|-----------|----------|---------|
| **OKR** | Para onde a organização vai? | Estratégia (trimestre/ano) |
| **RICE** | Qual feature traz mais valor relativo? | Discovery / roadmap |
| **WSJF** | O que entra no próximo PI/sprint? | Ordenação com pressão de prazo |

Camadas complementares: **OKR** define resultado estratégico → **RICE/WSJF** ordena backlog → **Status Report** comunica progresso dos KRs.

---

## 3. Exemplo RouteWise

### OKR 1 — Segurança

**Objective:** Tornar a frota RouteWise mais segura e reduzir custos com sinistros.

| KR | Meta | Épico Jira |
|----|------|------------|
| KR 1.1 | Reduzir acidentes por excesso de velocidade em **20%** até set/2026 | `[EPIC] Segurança e Redução de Sinistros` |
| KR 1.2 | Reduzir eventos de condução de risco (score comportamental) | US-03 Score (bloqueada hardware v2) |

### OKR 2 — Manutenção

**Objective:** Reduzir custo operacional com manutenção inteligente.

| KR | Meta | Épico Jira |
|----|------|------------|
| KR 2.1 | Reduzir custo médio de manutenção corretiva por veículo em **15%** | `[EPIC] Manutenção Inteligente` |

---

## 4. Rastreabilidade discovery → OKR → Jira → Status Report

```mermaid
flowchart LR
  D[Discovery Carlos] --> E[Épicos Copilot]
  E --> O[OKRs M10]
  O --> J[Issues Jira]
  J --> S[Status Report M07]
  S --> B[Board julho]
```

Na discovery, Carlos pedia relatório semanal para o diretor — o **Status Report** (M07) mede progresso dos **KRs** definidos aqui.

---

## 5. Critérios de bons KRs

- **Mensurável:** número + baseline + prazo (não "melhorar segurança")
- **Verificável:** ligado a stories com Gherkin testável
- **Ambicioso mas alcançável:** típico 60–70% de atingimento = sucesso
- **Limitado:** 2–4 KRs por Objective

---

## 6. Relação com outros relatórios

| Relatório | Conexão |
|-----------|---------|
| [`RELATORIO_M01_REQUISITOS_IA.md`](./RELATORIO_M01_REQUISITOS_IA.md) | Épicos originados na discovery |
| [`RELATORIO_M07_STATUS_REPORTS_IA.md`](./RELATORIO_M07_STATUS_REPORTS_IA.md) | Progresso dos KRs no Sprint 4 |
| [`RELATORIO_RICE_VS_WSJF.md`](./RELATORIO_RICE_VS_WSJF.md) | Priorização alinhada a OKR |
| [`RELATORIO_M10_PORTFOLIO_OKRS_IA.md`](./RELATORIO_M10_PORTFOLIO_OKRS_IA.md) | OKR Aligner, portfólio, demo M10.2 |

---

*Relatório elaborado para o repositório pos-unipds-IA · Módulo 7 — Gestão de Projetos com IA*
