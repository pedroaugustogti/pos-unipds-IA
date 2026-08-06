# Evidências de Execução — Lab 9 (FinOps Cloud)

Validação executada em **2026-08-06** (reexecução com cálculo determinístico).

**Relatório didático:** [`RELATORIO_DIDATICO_MODULO9.md`](./RELATORIO_DIDATICO_MODULO9.md)

---

## Objetivo do lab

Pipeline CrewAI com auditoria FinOps e **validação programática** dos totais:

1. **Consultor de FinOps Cloud** — invoca `analyze_cloud_costs`
2. Tool calcula zumbis (custo integral) e rightsizing (economia parcial)
3. Agente apresenta relatório executivo com subtotais corretos
4. Script valida `$55 + $270 = $325` deterministicamente

Script: `nexus/labs/modulo9_finops.py`  
Tool: `nexus/tools/finops_tools.py`

---

## Ambiente

| Item | Valor |
|------|-------|
| Python | 3.12.10 (venv) |
| CrewAI | 1.15.11 |
| LLM | Groq `llama-3.1-8b-instant` |
| Entrada | `nexus/data/inventario_cloud.json` |
| Conta simulada | `123456789012` · `us-east-1` |
| Data | 2026-08-06 |
| Duração | **~8 s** |
| Exit code | **0** ✅ |

### Comando

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
.\venv\Scripts\Activate.ps1
python labs/modulo9_finops.py
```

---

## Resultado da execução

| Métrica | Valor |
|---------|-------|
| **Exit code** | `0` ✅ |
| **Tasks concluídas** | **1/1** |
| **Tool calls** | **1** (`analyze_cloud_costs`) |
| **Validação determinística** | **Passou** ✅ |

---

## Ajustes implementados (revisão de cálculo)

| Problema anterior | Correção |
|-------------------|----------|
| Soma zumbis incorreta ($55 volumes + $5 IP duplicado) | Tool separa EBS ($50) + EIP ($5) → subtotal **$55** |
| EC2 com economia = $340 (eliminação total) | Rightsizing: **$340 − $70** = **$270** (downsize para `m5.large`) |
| LLM recalculava valores | Cálculo em `finops_tools.py`; agente só apresenta subtotais da tool |
| Total errado ($400) | Total correto: **$325/mês** |

### Metadados adicionados ao inventário EC2

```json
"recommended_instance_type": "m5.large",
"rightsized_cost_per_month": 70.00
```

---

## Saída da tool (cálculo determinístico)

```
=== ZUMBIS (economia = custo integral — delete/release) ===
- vol-0a1b2c3d [EBS órfão]: $50.00/mês → Snapshot opcional + DeleteVolume
- eipalloc-001122 [Elastic IP solto]: $5.00/mês → ReleaseAddress
Subtotal zumbis: $55.00/mês

=== RIGHTSIZING (economia = custo atual − custo após downsize) ===
- i-99887766 m5.4xlarge (CPU 2.5%): $340.00 → m5.large $70.00 | economia $270.00/mês
Subtotal rightsizing: $270.00/mês

ECONOMIA TOTAL ESTIMADA: $325.00/mês
(Zumbis $55.00 + Rightsizing $270.00)
```

---

## Resposta do agente

> Relatório FinOps com zumbis **$55/mês**, rightsizing **$270/mês**, total **$325/mês**.

Alinhado 100% com os subtotais da tool.

---

## Validação programática (pós-execução)

```
============================================================
📋 VALIDAÇÃO FINOPS (CÁLCULO DETERMINÍSTICO)
============================================================

✅ Zumbis: $55.00/mês
✅ Rightsizing: $270.00/mês
✅ Total: $325.00/mês
```

| Verificação | Esperado | Obtido |
|-------------|----------|--------|
| Zumbis detectados | 2 | 2 ✅ |
| Rightsizing detectado | 1 | 1 ✅ |
| Subtotal zumbis | $55.00 | $55.00 ✅ |
| Subtotal rightsizing | $270.00 | $270.00 ✅ |
| Total | $325.00 | $325.00 ✅ |

---

## Detalhamento financeiro

| Recurso | Tipo | Ação | Economia/mês | Categoria |
|---------|------|------|--------------|-----------|
| `vol-0a1b2c3d` | EBS `available` | DeleteVolume | **$50.00** | Zumbi (integral) |
| `eipalloc-001122` | EIP `unassociated` | ReleaseAddress | **$5.00** | Zumbi (integral) |
| `i-99887766` | `m5.4xlarge` → `m5.large` | Rightsizing | **$270.00** | Parcial ($340−$70) |
| | | **TOTAL** | **$325.00** | |

### Cortes por urgência

| Prioridade | Economia | Risco | Prazo |
|------------|----------|-------|-------|
| **P0 — Zumbis** | $55/mês | Baixo | Imediato |
| **P1 — Rightsizing** | $270/mês | Médio (janela de manutenção) | Planejado |

---

## Critérios de aceite

- [x] Execução sem erro Groq
- [x] Tool `analyze_cloud_costs` (1×)
- [x] Zumbis: EBS + EIP = **$55** (sem dupla contagem)
- [x] Rightsizing EC2: **$270** (não $340)
- [x] Total: **$325**
- [x] Validação automática no script

---

## Conclusão

Após os ajustes em `finops_tools.py`, o Lab 9 produz **cálculos FinOps corretos e auditáveis**:

- **Zumbis:** economia = custo integral recuperável ($55)
- **Rightsizing:** economia = diferença pós-downsize ($270), não eliminação total da instância
- **Total:** $325/mês com validação programática ao final do pipeline

---

## Próximo passo

Lab 10 — RAG & Runbooks: [`modulo10_remediation.py`](../nexus/labs/modulo10_remediation.py)

---

## Referências

| Recurso | Caminho |
|---------|---------|
| Script | [`nexus/labs/modulo9_finops.py`](../nexus/labs/modulo9_finops.py) |
| Tool FinOps | [`nexus/tools/finops_tools.py`](../nexus/tools/finops_tools.py) |
| Inventário | [`nexus/data/inventario_cloud.json`](../nexus/data/inventario_cloud.json) |
| Relatório didático | [`RELATORIO_DIDATICO_MODULO9.md`](./RELATORIO_DIDATICO_MODULO9.md) |
