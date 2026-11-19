# 3.6 (extra) — CI: `-p`, JSON schema, findings, instances

> Cruza com [36-cicd-claude-code.md](./36-cicd-claude-code.md).

## Cenário A — CI trava esperando input

`claude "Review…"` sem `-p` → pede permissão/pergunta → job pendura.

| Não | Sim |
|-----|-----|
| Timeout maior | **`claude -p` / `--print`** + permissions pré-aprovadas |

---

## Cenário B — Review repete comments

Cada run = sessão nova. “Avoid duplicates” sem lista = soft.

**Padrão:** guardar findings (artifact / comments) e **injetar no prompt** da próxima run.

```text
Run N   → review.json → artifact
Run N+1 → PREV no prompt → só delta
(+ script: to_comment = after - before)
```

Store típico: `actions/upload-artifact` com `review.json` (`rule_id+file+line`).

---

## Três peças juntas

1. `--output-format json` + `--json-schema` → parseável  
2. Passar **tests + previous findings** no prompt  
3. Review em **instance separada** (não self-review na sessão que implementou)

---

## Como “criar” session por job

Cada `claude -p` **já é** session nova. Não use `--resume` entre implement e review.

```text
Job A (dev): implement + push
Job B: claude -p correctness   ← sem --resume
Job C: claude -p security      ← outro processo/prompt
gate.py agrega JSON
```

Isolamento = processo novo + prompt novo (+ jobs paralelos).  
Estado entre runs = **artifacts no prompt**, não resume de chat.

Exemplo YAML didático: ver bloco em revisão da sessão / `exemplos/ci-pr-claude.yml`.

---

## Checkpoint

- [ ] `-p` no CI
- [ ] Findings anteriores no prompt
- [ ] Instance separada para review
- [ ] Sem `--resume` implement→review

← [3.6](./36-cicd-claude-code.md) · [ESTUDO](./ESTUDO.md)
