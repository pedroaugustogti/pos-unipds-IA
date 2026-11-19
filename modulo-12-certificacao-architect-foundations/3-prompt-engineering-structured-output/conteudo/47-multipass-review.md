# 4.6 — Multi-Instance and Multi-Pass Review

> Task statement (CertPrep): [Multi-Instance and Multi-Pass Review](https://certprep.pratechlabs.com/claude/ccar-f/learn/4-prompt-structured-output/4-6-multi-pass-review/)  
> Domínio D4 · 20%

## Objetivo
Evitar self-review na mesma sessão; usar instância independente e/ou vários passes com critérios distintos; confidence nos findings para o humano priorizar.

## Analogia
Autor não é o único revisor do próprio artigo na mesma sentada. Outro revisor (ou outro checklist) vê vieses.

## Padrões

| Situação | Escolha |
|----------|---------|
| PR pequeno / focado | Single-pass pode bastar |
| PR grande / multi-domínio | Multi-pass (security → correctness → tests) |
| Mesma sessão gerou o código | **Nova instância** para review |
| Achados demais | Cada finding com confidence; humano olha duvidosos primeiro |

## Exemplo prático — CI
```text
Pass A (sessão nova): security criteria → findings JSON
Pass B (sessão nova): correctness / missing tests
Host agrega, deduplica, ordena por confidence
```

Anti-padrão: “pensa mais” na mesma thread que escreveu o código.

## Mini-lab
Desenhe 2 passes para mudança em `auth/` + schema mínimo do finding.

## Checkpoint
- [ ] Same-session self-review = errado
- [ ] Multi-pass com critérios explícitos (liga 4.1)

← [4.5](./46-batch-processing.md) · [ESTUDO](./ESTUDO.md)
