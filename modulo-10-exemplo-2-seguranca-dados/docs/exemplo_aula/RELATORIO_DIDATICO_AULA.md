# Relatório Didático — Segurança de dados

> Aula `modulo-10-exemplo-2-seguranca-dados`  
> Caso: segurança como ataque e defesa contínuos, e texto recuperado que tenta anular uma regra de negócio.

Fontes: `[manual_seguranca_aula.pdf](../../materiais_aula/manual_seguranca_aula.pdf)` e `[Demonstração.ipynb](../../materiais_aula/Demonstração.ipynb)`.

## Objetivo

Distinguir avaliação pontual, exercício adversário e defesa contínua, e ver no notebook por que uma instrução de sistema não basta quando o dado recuperado traz outra ordem.

## Manual — o tabuleiro

O manual trata a segurança como processo, não como estado. Três papéis e um quarto que é colaboração, não um time novo.


| Papel       | O que faz                                                                                                               | O que entrega                                    |
| ----------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Pentest     | Ataque simulado, autorizado, com escopo fechado (uma API, um bloco de IPs)                                              | Relatório de brechas e correção                  |
| Red Team    | Adversário persistente atrás de um objetivo (servidor central, dado confidencial), inclusive engenharia social e evasão | Diagnóstico de prontidão, processos e pessoas    |
| Blue Team   | Defesa contínua: tráfego, logs, SIEM, firewall, privilégio mínimo, criptografia                                         | Detectar, conter e remediar sem parar a operação |
| Purple Team | O Red descreve o caminho logo após o exercício; o Blue ajusta a detecção para aquele método                             | Maturidade, não um organograma novo              |


A metáfora do manual para o Pentest é o chaveiro contratado para testar fechaduras e listar as frágeis. O Red Team não para na porta aberta: observa rotina, disfarce e processo humano. O Blue Team precisa manter a operação íntegra enquanto isso ocorre.

## Demonstração

Notebook educacional, no Colab, com `GEMINI_API_KEY` nos Secrets e o modelo `gemini-2.5-flash`. A regra de negócio fica em `system_instruction`. O histórico do cliente entra em `contents`.


| Bloco            | Contraste                                                                                                                                           |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Injeção indireta | Histórico legítimo de um cliente premium contra um histórico de cliente bloqueado que embute uma instrução para ignorar a regra e conceder vantagem |
| Regra            | Cliente bloqueado não recebe cupom nem vantagem                                                                                                     |
| Jailbreak        | Pedido direto barrado pelo filtro contra o mesmo intento reescrito como personagem de ficção                                                        |


A separação entre instrução de sistema e texto recuperado não impede o segundo texto de tentar comandar o atendimento.

## Camadas


| Camada           | Artefato                                     | Papel                                       |
| ---------------- | -------------------------------------------- | ------------------------------------------- |
| 2.1 Manual       | `manual_seguranca_aula.pdf`                  | Pentest, Red, Blue, Purple e a matriz       |
| 2.2 Demonstração | `Demonstração.ipynb`                         | Injeção indireta e jailbreak por personagem |
| 2.3 Leitura      | `[SEGURANCA_DADOS.md](./SEGURANCA_DADOS.md)` | O que registrar dos dois materiais          |
| 2.4 Temas        | `[TEMAS_DA_AULA.md](./TEMAS_DA_AULA.md)`     | Tensões do tabuleiro e da demonstração      |




## Ponte


| Exemplo           | Ligação                                                                                |
| ----------------- | -------------------------------------------------------------------------------------- |
| Ex.1 deste módulo | Quem publica o sistema continua responsável pelo efeito                                |
| Guardião          | `[../exemplo_real/01-guardiao/aplicacao.md](../exemplo_real/01-guardiao/aplicacao.md)` |


