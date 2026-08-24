# Relatorio Didatico — 2 Single Agent

> Gerado pelo **delivery-agent** apos o scaffold da proxima aula.
> Pasta: `modulo-8-exemplo-2-single-agent` | Modulo 8 Exemplo 2 | [modulo-8-exemplo-2-single-agent](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo08-arquitetura-de-sistemas-com-ia/2-single-agent)

---

## Resumo visual

### Arquitetura do exemplo

```mermaid
flowchart TB
  UNIPDS["UNIPDS<br/>modulo-8-exemplo-2-single-agent"]
  SCAFFOLD["Scaffold<br/>modulo-8-exemplo-2-single-agent"]
  RUNTIME["runtime/main.py"]
  UNIPDS --> SCAFFOLD --> RUNTIME
  OUT["trace / relatorio / JSON"]
  RUNTIME --> OUT
```

### Fluxo de preparacao

```mermaid
sequenceDiagram
  participant U as Voce
  participant D as delivery-agent
  participant G as GitHub UNIPDS
  participant R as Repo local
  U->>D: preparar proxima aula
  D->>R: verificar_aula_atual_pronta
  D->>R: executar_commit_push_aula_atual
  D->>G: baixar_base_unipds
  G-->>R: scaffold
  D->>R: gerar_relatorio_didatico_aula
  Note over D: relatorio em texto (saida do agente)
```

### Mapa do scaffold

```
modulo-8-exemplo-2-single-agent/
├── README.md
└── ... (17 arquivos)
```

---

## Principais topicos abordados

### 1. Anatomia do agente

Componentes: LLM, tools, memoria, planner e loop de execucao.

**Exemplo de uso:**
```bash
python agent_components_demo.py
```

### 2. ReAct loop

Raciocinio + acao iterativo com tool schemas tipados.

**Exemplo de uso:**
```bash
python react_agent_prototype.py
```

### 3. Reflection e tools

Prompts de reflexao e contratos de tool (JSON schema).

**Exemplo de uso:**
```bash
cat reflection-prompt-canvas.md tool-schema-canvas.md
```


---

## Secoes do README local

- Objetivo
- Pré-requisitos
- Configuração
- Como executar
- Critérios de sucesso

---

## Comandos CLI detectados

| Comando | Uso |
|---------|-----|
| `rodar` | `python main.py rodar --agente ../monitor-agent` |
| `validar` | `python main.py validar --agente ../monitor-agent` |


---

## Arquivos-chave

- (estrutura em construcao)

---

## Proximos passos

1. Leia `README.md` e o material UNIPDS
2. Configure `.env` (nunca commite segredos)
3. `python main.py validar --agente ../monitor-agent`
4. Execute a atividade e valide criterios de sucesso

---

*Gerado por `gerar_relatorio_didatico_aula` (delivery-agent).*
