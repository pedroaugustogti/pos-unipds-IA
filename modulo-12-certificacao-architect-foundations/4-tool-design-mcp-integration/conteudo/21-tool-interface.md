# 2.1 — Design da interface da tool

## Objetivo
Escrever description + schema que o modelo seleciona certo — description e criterio de selecao.

## Analogia
Rotulo de gaveta no escritorio: "Canetas pretas — NAO grampos".

## Checklist da description
1. Proposito e **quando** usar
2. Input (exemplos)
3. Output
4. Edge cases
5. Diferenca vs tools parecidas

## Exemplo
**Ruim:** `"search": "Search for things"`

**Bom:**
```json
{
  "name": "search_knowledge_base",
  "description": "Busca artigos internos de suporte/FAQ. Use para duvidas de produto/policy. NAO use para status de pedido (use lookup_order).",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Pergunta em linguagem natural, ex. 'prazo de troca eletronicos'"}
    },
    "required": ["query"]
  }
}
```

Overlap `analyze_content` vs `analyze_document` → renomear/fundir.

## Mini-lab
Reescreva 2 tools ambiguas do seu dominio.

## Checkpoint
- [ ] Description com quando usar / nao usar
- [ ] Schema com required minimo

← [ESTUDO](./ESTUDO.md) · → [2.2](./22-erros-estruturados.md)
