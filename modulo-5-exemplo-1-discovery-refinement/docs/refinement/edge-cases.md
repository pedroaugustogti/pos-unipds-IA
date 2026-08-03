# Edge cases — Pix Agendado

> **Status:** Artefato de saída do refinamento — ver `PIPELINE.md`.

**Input:** `briefing-bruto.md`  
**Prompt:** `prompts/system-instructions-refinement.md`

---

## 1. Análise de risco (pontos cegos)

| Risco | Impacto | Mitigação sugerida |
|-------|---------|-------------------|
| Limite noturno BCB (20h–06h, ~R$ 1.000) | Agendamento aprovado na UI mas rejeitado na execução | Validar limite no horário de liquidação, não só no ato do agendamento |
| Janela de cancelamento indefinida | Usuário tenta cancelar Pix já em processamento | Estado `CANCEL_LOCKED` + regra explícita (ex.: até D-1 23:59) |
| Chave Pix desatualizada entre agendamento e execução | Falha silenciosa na liquidação | Estado de alerta na lista de agendamentos |
| Ausência de MFA no requisito | Risco de fraude / não conformidade | Biometria ou senha transacional antes do POST |
| Concorrência de saldo futuro | Múltiplos agendamentos no mesmo dia excedem saldo | Motor define prioridade (FIFO ou valor) + aviso soft na UI |

---

## 2. Cenários ocultos (unhappy paths)

### Entrada e validação
- Valor > R$ 5.000,00 → erro inline, botão Continuar desabilitado
- Data = hoje → sugestão de redirecionamento para Pix imediato (herdar contato/valor)
- Data passada → bloqueio no date picker + mensagem de data retroativa
- Dia 31 em mês de 30 dias → crash (bug reportado em tkt_05) — validar `max days` no calendário
- Lista de contatos vazia → empty state + busca manual por chave Pix
- Chave inválida / destinatário não encontrado → erro antes da revisão

### Processamento
- MFA falha → retry sem perder dados da revisão
- API 403 (saldo / risco) → erro de negócio com retorno à revisão
- API 429/500 → instabilidade Bacen, opção tentar novamente
- Timeout → orientar verificar extrato (idempotência via `x-idempotency-key`)
- Tela branca no fluxo Pix (tkt_01) → Error Boundary no front-end

### Pós-sucesso e cancelamento
- Comprovante difícil de achar (tkt_06) → atalho na home + CTA no comprovante
- Cancelamento com agendamento em liquidação → erro `CANT_CANCEL_TODAY`
- Cancelamento com sucesso → toast + atualização da lista

---

## 3. Regras de negócio conflitantes

| Regra no briefing | Conflito | Resolução proposta |
|-------------------|----------|-------------------|
| Limite diário R$ 5.000 | Limite noturno menor na execução | Dois limites: criação vs liquidação |
| Não agendar para hoje | Usuário pode querer Pix imediato | Fluxo alternativo Pix normal, não apenas erro |
| Botão cancelar depois | Sem prazo definido | Documentar SLA de cancelamento |

---

## 4. Considerações para front-end

1. **Redirecionamento inteligente** — data = hoje → botão "Fazer Pix agora"
2. **Acessibilidade** — date picker navegável por teclado; leitor de tela anuncia data futura
3. **Idempotência** — header `x-idempotency-key` no POST de agendamento
