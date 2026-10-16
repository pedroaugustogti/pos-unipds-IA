# Artefato de aula — segurança de dados

| Peça | Onde |
|------|------|
| Manual | [`manual_seguranca_aula.pdf`](../../materiais_aula/manual_seguranca_aula.pdf) |
| Demonstração | [`Demonstração.ipynb`](../../materiais_aula/Demonstração.ipynb) |

A demonstração é educacional. Roda no Colab com `GEMINI_API_KEY` e o modelo `gemini-2.5-flash`.

## O que registrar no manual

| Pergunta | O que o manual mostra |
|----------|------------------------|
| Pentest é o quê? | Avaliação pontual, autorizada, escopo fechado, relatório de vulnerabilidade |
| Red Team muda o quê? | O alvo vira um objetivo; o exercício fica oculto para a maior parte da organização e inclui pessoas e processos |
| Blue Team opera quando? | O tempo todo: monitorar, detectar, conter, remediar |
| Quem sabe do exercício? | Pentest é conhecido pela TI; Red Team não; Blue Team está na rotina |
| Purple Team é um quarto departamento? | Não. É o Red contando o caminho e o Blue fechando a detecção daquele método |

## O que registrar na demonstração

| Bloco | O que comparar |
|-------|----------------|
| Injeção indireta | Atendimento com histórico limpo contra atendimento cujo histórico traz uma instrução |
| Onde está a regra | `system_instruction`: cliente bloqueado não recebe vantagem |
| Onde está o ataque | `contents`: o texto “recuperado do banco” manda ignorar a regra |
| Jailbreak | Pedido direto contra o mesmo intento vestido de ficção |

Temas: [`TEMAS_DA_AULA.md`](./TEMAS_DA_AULA.md). Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md).
