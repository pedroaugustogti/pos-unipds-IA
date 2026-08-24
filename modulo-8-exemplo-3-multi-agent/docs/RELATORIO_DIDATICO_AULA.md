# Relatorio Didatico — 3 Multi Agent

> Gerado pelo **delivery-agent** apos o scaffold da proxima aula.
> Pasta: `modulo-8-exemplo-3-multi-agent` | Modulo 8 Exemplo 3 | [modulo-8-exemplo-3-multi-agent](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo08-arquitetura-de-sistemas-com-ia/3-multi-agent)

---

## Resumo visual

### Arquitetura do exemplo

```mermaid
flowchart TB
  UNIPDS["UNIPDS<br/>modulo-8-exemplo-3-multi-agent"]
  SCAFFOLD["Scaffold<br/>modulo-8-exemplo-3-multi-agent"]
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
modulo-8-exemplo-3-multi-agent/
├── README.md
└── ... (11 arquivos)
```

---

## Principais topicos abordados

### 1. Fronteiras multi-agent

Delimitar responsabilidades, estado e contratos entre agentes.

**Exemplo de uso:**
```bash
cat multi-agent-boundary-canvas.md
```

### 2. Orquestracao e filas

Seletor de padrao (sequencial, paralelo, hierarquico) + message queue.

**Exemplo de uso:**
```bash
python trialforge_message_queue_prototype.py
```

### 3. Falhas distribuidas

Canvas de failure modes, retry e compensacao entre agentes.

**Exemplo de uso:**
```bash
cat distributed-failure-canvas.md orchestration-pattern-selector-v2.md
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
