# Relatorio Didatico — LoRA e PEFT

> Gerado pelo **delivery-agent** apos o scaffold da proxima aula.
> Pasta: `modulo-9-exemplo-4-lora-e-peft` | Modulo 9 Exemplo 4 | [modulo-04-lora-e-peft](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-04-lora-e-peft)

---

## Resumo visual

### Arquitetura do exemplo

```mermaid
flowchart TB
  UNIPDS["UNIPDS<br/>modulo-04-lora-e-peft"]
  SCAFFOLD["Scaffold<br/>modulo-9-exemplo-4-lora-e-peft"]
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
modulo-9-exemplo-4-lora-e-peft/
├── README.md
└── ... (39 arquivos)
```

---

## Principais topicos abordados

### 1. LoRA vs full FT

Tradeoff de rank, VRAM e qualidade; adapters PEFT.

**Exemplo de uso:**
```bash
python full_vs_lora_tradeoff_tool.py && python adapter_comparison_tool.py
```

### 2. Treino local/Colab

Notebooks e tools HF para treinar LoRA sem cluster.

**Exemplo de uso:**
```bash
python local_lora_training_tool.py
```

### 3. Config de rank

YAML de rank 16 e preview de API gerenciada LoRA.

**Exemplo de uso:**
```bash
cat lora-rank16-config.yaml
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
