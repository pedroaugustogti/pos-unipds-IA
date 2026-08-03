# PAPEL
Atue como Engenheiro Front-end Sênior especialista em testes Angular com Vitest.

# OBJETIVO
Criar testes unitários para `PixReceiptComponent` em `features/receipt/`.

# CASOS OBRIGATÓRIOS
1. Renderiza valor formatado em BRL (`R$ 150,00` para input `150`).
2. Exibe nome do recebedor (`Erick S.`).
3. Emite `voltarInicio` ao clicar em **Voltar ao Início**.
4. Exibe `transactionId` quando fornecido.
5. Ícone `check_circle` presente no DOM.

# REGRAS
- Use `TestBed` com componente standalone.
- Não mockar o DOM inteiro; teste interação real do botão.
- Arquivo sugerido: `features/receipt/pix-receipt.component.spec.ts`
- Gates: `npm test -- --watch=false` e `npm run build`

# FORMATO DE SAÍDA
Arquivo `.spec.ts` completo + resumo dos casos cobertos.
