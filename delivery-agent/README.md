# delivery-agent

Agente de entrega do repositório **pos-unipds-IA** — compara UNIPDS vs local, baixa base da próxima aula, cria pasta `modulo-X-exemplo-Y`, customiza READMEs e prepara commit (sem PR).

**Runtime:** [`modulo-4-exemplo-1-agente-ia-contratos/runtime/`](../modulo-4-exemplo-1-agente-ia-contratos/runtime/)

## Estrutura

```
delivery-agent/
├── agent.md          # identidade e contrato de saída
├── skills.md         # ferramentas disponíveis
├── rules.md          # políticas e limites
├── hooks.md          # ganchos do ciclo
├── memory.md         # memória curta
└── contracts/
    ├── planner.md
    ├── executor.md
    ├── loop.md
    └── toolbox.md
```

## Como executar

```bash
cd modulo-4-exemplo-1-agente-ia-contratos/runtime
python main.py validar --agente ../../delivery-agent
python main.py rodar --agente ../../delivery-agent --entrada "modulo 5: preparar proxima aula"
```

### Orquestração direta (sem LLM)

```bash
cd modulo-4-exemplo-1-agente-ia-contratos/runtime
python run_delivery_modulo5.py    # módulo 5
python run_delivery_modulo6.py  # módulo 6 (Nexus AI-Ops)
python run_delivery_modulo7.py  # módulo 7 M01
python run_delivery_modulo8.py    # módulo 8 completo (5 exemplos TrialForge)
python run_delivery_proxima_aula.py  # módulo 4 (padrão)
```

## Fluxo

`comparar_repositorios` → `verificar_aula_atual_pronta` → `executar_commit_push_aula_atual` (se necessário) → `identificar_proximo_exemplo` → `baixar_base_unipds` → `customizar_readme_exemplo` → `atualizar_readme_raiz` → `gerar_relatorio_didatico_aula` → `garantir_readmes_para_commit` → `preparar_mensagem_commit`

## Origem

Customização da Opção C do [Módulo 4 — Exemplo 1](../modulo-4-exemplo-1-agente-ia-contratos/) (contratos de agente UNIPDS).
