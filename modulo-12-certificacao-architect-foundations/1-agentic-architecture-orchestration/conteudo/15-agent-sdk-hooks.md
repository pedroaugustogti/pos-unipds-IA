# 1.5 — Agent SDK Hooks: Interception and Normalization

> Task: [Agent SDK Hooks](https://certprep.pratechlabs.com/claude/ccar-f/learn/1-agentic-architecture/1-5-hooks/)

## Objetivo de aprendizado

Usar hooks nos pontos fixos do loop: **PreToolUse** (bloquear/redirecionar/reescrever antes de executar) e **PostToolUse** (normalizar/trimar resultado antes do modelo ver). Regra “must always/never” → hook, não prompt.

## Analogia didática

Placa “não ultrapasse 60 km/h” (prompt) vs **radares que multam** (hook).

O modelo pode “esquecer” a placa. O radar não negocia.

## Tabela mental

| | Prompt / CLAUDE.md / system | Hook / policy engine |
|--|----------------------------|----------------------|
| Natureza | Melhor esforço | Determinístico |
| Quando falha | Modelo ignora / reinterpretar | Código bloqueia |
| Uso | Estilo, preferências, “tente X” | Money, delete, prod, secrets |
| Audit | Fraco | Logável / testável |
| Resposta CCAR-F para regra crítica | ❌ “adicionar no system” | ✅ hook ou gate |

## Exemplo prático — Claude Code / Agent SDK

### Só prompt (insuficiente para regra crítica)

```markdown
<!-- CLAUDE.md -->
Nunca rode `git push --force` em main.
Nunca delete arquivos em /prod.
```

Útil como guidance — **não** basta se a prova fala em enforcement.

### Hook que garante

```json
// settings — ideia didática de PreToolUse / permission hook
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python hooks/block_dangerous.py"
          }
        ]
      }
    ]
  }
}
```

```python
# hooks/block_dangerous.py — conceitual
import json, sys, re

payload = json.load(sys.stdin)
cmd = payload.get("tool_input", {}).get("command", "")

DENY = [
    r"git\s+push\s+.*--force",
    r"\brm\s+-rf\s+/",
    r"kubectl\s+delete\s+.*prod",
]

for pat in DENY:
    if re.search(pat, cmd):
        print(json.dumps({
            "decision": "deny",
            "reason": f"blocked by policy hook: {pat}",
        }))
        sys.exit(0)

print(json.dumps({"decision": "allow"}))
```

No **Agent SDK / app própria**, o equivalente é um gate **antes** de executar a tool:

```python
def before_tool(name: str, args: dict) -> None:
    if name == "process_refund" and args.get("amount", 0) > 100:
        raise HitlRequired("refund over limit — pause for human")
    if name == "bash" and is_dangerous(args.get("command", "")):
        raise PermissionError("blocked by host policy")
```

## Quando prompt ainda é o certo

- “Prefira TypeScript strict”
- “Responda em pt-BR”
- “No review, ignore typos em comentários”
- Convenções de código do time

Prompt molda comportamento; hook **impede** ação.

## Mini-lab

Classifique cada regra:

1. “Não commitar secrets”  
2. “Usar Conventional Commits”  
3. “Refund > $100 precisa humano”  
4. “Tom amigável no suporte”  
5. “Proibido `DROP TABLE` via Bash”

Respostas esperadas: 1 hook (+ scan), 2 prompt, 3 hook/HITL, 4 prompt, 5 hook.

## Pegadinha clássica

> “O agente às vezes processa refund acima do limite. Como corrigir?”

| Opção | Veredito |
|-------|----------|
| Reforçar system prompt “nunca passe de 100” | Fraco |
| Fine-tune | Fora de escopo / overkill |
| **Hook/gate que bloqueia ou pausa HITL** | Certo |
| Remover a tool | Pode ser certo se não precisa; geralmente pior que gate |

## Checkpoint

- [ ] Frase pronta: **prompt sugere, hook garante**
- [ ] Dou 3 exemplos de cada
- [ ] Ligo HITL (1.4) com hook (1.5) no refund

← [1.4 HITL](./14-workflow-enforcement-hitl.md) · [Índice](./ESTUDO.md) · → [1.6 Decomposição](./16-task-decomposition.md)
