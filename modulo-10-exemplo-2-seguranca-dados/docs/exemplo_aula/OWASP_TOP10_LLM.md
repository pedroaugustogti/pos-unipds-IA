# OWASP Top 10 para LLMs

Lista de 2025 das dez falhas mais graves em aplicações que usam modelo de linguagem. Cada item nomeia um risco. Os exemplos abaixo são casos públicos ou o próprio notebook desta aula.

Leitura da aula: `[SEGURANCA_DADOS.md](./SEGURANCA_DADOS.md)`. Demonstração: `[Demonstração.ipynb](../../materiais_aula/Demonstração.ipynb)`.


| #   | Risco                              | Definição                                                                                        | Exemplo                                                                                                                                                                                                      |
| --- | ---------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Prompt injection                   | Um texto faz o modelo trocar de tarefa. A ordem pode vir do usuário ou de um dado recuperado.    | No notebook, o histórico do cliente bloqueado traz uma instrução para anular a regra e conceder vantagem. O dado entra como contexto e passa a comandar o atendimento. O jogo [Gandalf](https://gandalf.lakera.ai/do-not-tell) (Lakera) é o mesmo risco em níveis: o modelo tem uma senha e a instrução é não revelá-la. |
| 2   | Vazamento de informação sensível   | O modelo devolve segredo que estava no treino, no prompt ou na conversa.                         | Em 2023, funcionários da Samsung colaram código-fonte e notas internas no ChatGPT. O conteúdo saiu do perímetro da empresa.                                                                                  |
| 3   | Cadeia de suprimentos              | O modelo, o adaptador, o pacote ou o plugin chega adulterado.                                    | Modelos e LoRAs publicados em repositório público já circularam com peso ou código trocado. Quem integra sem fixar origem e hash executa o artefato de outra pessoa.                                         |
| 4   | Envenenamento de dados e do modelo | O treino ou o ajuste fino aprende um comportamento plantado nos exemplos.                        | A Tay, da Microsoft (2016), passou a repetir ofensas horas depois de entrar no ar porque as mensagens do público viraram o sinal que ela imitava.                                                            |
| 5   | Saída mal tratada                  | A resposta do modelo é executada ou renderizada como se fosse código confiável.                  | Um chat que devolve HTML e a aplicação coloca isso direto na página abre script no navegador de quem lê. O modelo escreveu a string; o sistema é que a executou.                                             |
| 6   | Agência excessiva                  | O modelo pode chamar ferramenta com efeito irreversível, sem limite nem confirmação.             | Um agente com acesso a e-mail, reembolso ou shell envia a mensagem ou apaga o arquivo porque a resposta do modelo disparou a ferramenta.                                                                     |
| 7   | Vazamento do prompt de sistema     | A política interna do aplicativo é extraída na conversa.                                         | Em 2023, o prompt oculto do Bing Chat (Sydney), com regras e restrições, foi reproduzido por usuários no próprio chat.                                                                                       |
| 8   | Fraqueza de vetor e embedding      | O índice do RAG devolve um trecho adulterado e a aplicação trata esse trecho como fato ou ordem. | Um documento incluído na base passa a ser recuperado nas buscas e o assistente responde com o conteúdo plantado. É o mesmo desenho do histórico “vindo do banco” neste exemplo.                              |
| 9   | Desinformação                      | A resposta soa segura e está errada, e alguém age com base nela.                                 | Em Mata v. Avianca (2023), um advogado protocolou jurisprudência inventada pelo ChatGPT. Em 2024, um chatbot da Air Canada inventou uma regra de tarifa por luto e o tribunal manteve a empresa responsável. |
| 10  | Consumo sem limite                 | Uma entrada faz o modelo gerar demais, repetir chamadas ou estourar a conta da API.              | Um prompt longo, ou um agente em loop de ferramentas, gera uma fatura alta ou tira o serviço do ar para os outros usuários. O alvo é o custo e a disponibilidade.                                            |




## O que esta aula já cobre


| Item OWASP | Onde aparece aqui                                                                                                          |
| ---------- | -------------------------------------------------------------------------------------------------------------------------- |
| 1 e 8      | `[Demonstração.ipynb](../../materiais_aula/Demonstração.ipynb)`: regra na `system_instruction`, ataque no texto recuperado. Jogo: [Gandalf](https://gandalf.lakera.ai/do-not-tell) |
| 7          | A regra de negócio só protege o fluxo se continuar soberana e não for substituída pelo histórico                           |
| 6          | Controle local em `[02-demonstracao](../exemplo_real/02-demonstracao/README.md)`: o histórico não autoriza cupom           |


Relatório da aula: `[RELATORIO_DIDATICO_AULA.md](./RELATORIO_DIDATICO_AULA.md)`.