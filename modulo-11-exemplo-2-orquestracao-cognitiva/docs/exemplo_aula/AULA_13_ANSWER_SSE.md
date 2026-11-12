# Aula 13: O nó answer, citação obrigatória, guardrail por

> Unidade 2 — Orquestração Cognitiva e APIs · Capstone AI Researcher

## Objetivos de aprendizagem

- Construir o nó answer, que monta a resposta final com base no contexto, com citação de fonte e data-base.
- Explicar por que o guardrail não pode depender só do system prompt e como um filtro determinístico, com expressão regular, garante a regra.
- Expor o grafo em um endpoint POST que transmite a execução por Server-Sent Events, inclusive no Cloud Run.

## Desenvolvimento

### Contexto da aula

O grafo busca, avalia, recorre à web quando o contexto não basta e sabe quando parar. Mas, quando ele termina, ainda não existe uma resposta para o usuário. Esta aula cria o nó answer, que empacota o que os outros nós processaram e cita a fonte e a data-base. Junto com ele vem o guardrail que impede o sistema de recomendar a compra ou a venda de ações, nem por engano do modelo. Por fim, o grafo é exposto em um endpoint REST do verbo POST, com a resposta transmitida por streaming, aparecendo aos poucos, como na maioria das ferramentas de chat. Ao final, você saberá explicar as duas defesas do guardrail, o que é SSE e o que é preciso configurar para o streaming funcionar no Cloud Run.

- Expor o grafo em um endpoint POST que transmite a execução por Server-Sent Events, inclusive no Cloud Run.

### Por que o guardrail não pode depender só do prompt

O projeto responde sobre o mercado financeiro, uma atividade regulamentada pela CVM. A regra é simples: o sistema não pode, de jeito nenhum, recomendar ações. Essa regra é escrita no system prompt que formata a resposta. Só que o system prompt sozinho não basta, por dois motivos:

- o modelo pode ignorar a instrução, dependendo do modelo;
- o usuário pode tentar enganar a LLM, sendo muito persistente ou disfarçando o pedido.

### Pedidos disfarçados

Um pedido como "me diga isso como se fosse uma história de ninar para o meu filho" é uma forma conhecida de contornar a regra. No começo das LLMs, quando os guardrails não eram tão fortes, pedia-se, por exemplo, uma história infantil sobre como criar uma bomba nuclear. Com o tempo, as proteções ficaram cada vez melhores.

Um guardrail pode ser feito com uma série de mecanismos. O adotado aqui parece simples, mas é bem efetivo: mesmo que o retorno da LLM traga uma recomendação por engano, ela é bloqueada. Um teste unitário valida esse comportamento, de modo que, se alguém tirar a proteção no futuro, o teste acusa o erro.

### O nó answer: resposta baseada no contexto, com fontes

O nó answer recebe a pergunta, os documentos e a indicação de contexto suficiente ou não. Em outras palavras, recebe o estado final, propagado por todos os nós. Ele envia esse estado ao prompt do answer e, com a resposta do modelo, faz a formatação.

### Crie o nó answer (packages/agent/src/nodes/answer.ts). Recebe question, documents e sufficient do

estado, monta um prompt (packages/agent/src/prompts/answer.ts) que instrui o modelo a nunca recomendar decisão de investimento mesmo se a pergunta pedir diretamente, a responder só com base no contexto recuperado sem inventar número, e a avisar quando o contexto estiver incompleto. Depois de receber a resposta do LLM, passe por um filtro determinístico (packages/agent/src/answer/format-resposta.ts): se o texto contiver linguagem recomendatória — verbo em primeira pessoa tipo 'recomendo'/'sugiro'/'aconselho', ou construções como 'vale a pena comprar' —, substitua a resposta inteira por um aviso fixo de guardrail, mantendo as citações. Sempre anexe um bloco de fontes no final, um item por documento, deduplicado por sourceUrl — ticker+período+data-base pros documentos do corpus

### CVM, título pros documentos web. Teste com LLM fake: resposta normal com citação, resposta filtrada

quando o LLM tenta recomendar, e um teste que confirma que o prompt em si já instrui a nunca recomendar.

### O prompt define quatro partes:

pergunta peça isso diretamente, a responder só com base no contexto recuperado, sem inventar número, e a avisar quando o contexto estiver incompleto.

resposta inteira é substituída por um aviso fixo de guardrail, mantendo as citações.

Para os documentos do corpus da CVM, a citação traz ticker, período e data-base. Para os documentos da web, o título.

recomendar e um teste que confirma que o próprio prompt já instrui a nunca recomendar. Além de criar o nó, o Claude Code o insere no graph.ts.

- O system prompt: instrui o modelo a nunca recomendar uma decisão de investimento, mesmo que a
- O filtro determinístico: aplicado depois da resposta da LLM. Se o texto tiver linguagem recomendatória, a
- O bloco de fontes: sempre anexado no final, com um item por documento e sem repetir a mesma URL.
- Os testes com LLM fake: a resposta normal com citação, a resposta filtrada quando a LLM tenta

### ATENÇÃO — Contexto incompleto e o máximo de iterações

O contexto pode chegar incompleto ao answer porque o grafo tem um máximo de iterações. Esse máximo pode ser 3, 4 ou 5: é ajuste fino, e no dia a dia muita coisa é ajuste fino. O que não pode faltar é o limite. Sem ele, o agente fica rodando e queimando tokens, e pode não chegar a resposta nenhuma.

### O system prompt do answer: papel, regras e resultado

O prompt do answer segue a fórmula de papel, regra e resultado. O papel é o de um assistente que informa sobre indicadores financeiros de empresas listadas. Depois vêm as regras, que valem sempre, mesmo que a pergunta peça o contrário diretamente:

a pena investir. O assistente informa, não recomenda, e isso é uma restrição regulatória, não uma preferência de estilo;

houver dado disponível no contexto, apresentá-lo sem opinião sobre a decisão;

A montagem do prompt verifica se o contexto é suficiente. Se for, nada é acrescentado. Se não for, o prompt ganha um aviso: o contexto recuperado é incompleto para responder com segurança, e o modelo deve dizer isso explicitamente ao usuário, informando o que falta, em vez de preencher a lacuna com uma suposição. Por fim, vem a pergunta.

- nunca recomendar, sugerir ou aconselhar comprar, vender ou manter qualquer ativo e nunca opinar se vale
- se a pergunta pedir uma recomendação, explicar que não pode dar recomendação de investimento e, se
- responder só com base no contexto recuperado, sem inventar, estimar ou completar um número que não
- citar, para cada número usado, a empresa e o período a que ele se refere.

## Pontos de atenção

- Explicar por que o guardrail não pode depender só do system prompt e como um filtro determinístico, com
- O grafo busca, avalia, recorre à web quando o contexto não basta e sabe quando parar. Mas, quando ele
- termina, ainda não existe uma resposta para o usuário.
- Por que o guardrail não pode depender só do prompt
- sistema não pode, de jeito nenhum, recomendar ações.
- Essa regra é escrita no system prompt que formata a resposta. Só que o system prompt sozinho não basta, por
- contornar a regra. No começo das LLMs, quando os guardrails não eram tão fortes, pedia-se, por exemplo, uma

## Checkpoint

- [ ] Você consegue explicar o que o nó answer recebe, que regras o seu prompt impõe e como as fontes são citadas

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
