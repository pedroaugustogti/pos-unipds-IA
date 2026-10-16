# Temas da aula — tabuleiro e demonstração

O manual não numera questões de debate. Os temas saem da matriz (Pentest, Red Team, Blue Team, Purple Team) e dos dois contrastes do notebook.

Fontes: [`manual_seguranca_aula.pdf`](../../materiais_aula/manual_seguranca_aula.pdf) e [`Demonstração.ipynb`](../../materiais_aula/Demonstração.ipynb).

## Escopo fechado contra adversário persistente

O Pentest lista falhas dentro de um limite combinado e devolve um relatório. O Red Team mede se a organização percebe e reage quando o objetivo é outro (dado confidencial, servidor central) e o caminho inclui engenharia social e evasão. Achar a fechadura frágil não responde se alguém perceberia o disfarce.

## Defesa contínua contra exercício contratado

Pentest e Red Team entram e saem. O Blue Team permanece: tráfego, log, SIEM, firewall, privilégio mínimo, criptografia, e a operação tem de seguir íntegra durante o ataque. O tema é que o relatório ofensivo só vale se a defesa mudar a rotina, não se o PDF for arquivado.

## Purple Team

Não é um time extra. Depois do exercício, o lado ofensivo descreve o caminho e o lado defensivo ajusta a detecção para aquele método deixar de funcionar. A maturidade depende dessa troca. Sem ela, o Red repete o mesmo caminho e o Blue continua cego para ele.

## Regra de sistema contra dado recuperado

No notebook, a política do atendimento é soberana no texto: cliente bloqueado não ganha vantagem. O histórico legítimo só descreve o cliente. O histórico do atacante traz, no meio do dado, a ordem de ignorar a regra. Os dois entram como “histórico recuperado do banco”. O tema é que conteúdo recuperado não é instrução, e colocar a regra só na `system_instruction` não garante isso.

## Filtro nativo contra reescrita de personagem

O segundo bloco compara um pedido direto, que o filtro do modelo tende a recusar, com o mesmo intento reescrito como cena de ficção. O tema é que a trava nativa olha a forma do pedido. Trocar o enquadramento não muda o que se pede. A aula marca o contraste; não é um roteiro para repetir o pedido.

## O que a aula não fecha

| Tema | Tensão que permanece |
|------|----------------------|
| Pentest e Red Team | Lista de falhas no escopo contra prontidão de pessoas e processos |
| Blue Team | Exercício pontual contra monitoração que não pode parar |
| Purple Team | Sigilo do exercício contra a necessidade de contar o caminho para a defesa |
| Injeção indireta | Regra escrita no sistema contra ordem escondida no dado |
| Jailbreak | Recusa do pedido direto contra o mesmo pedido em outro gênero |

Leitura: [`SEGURANCA_DADOS.md`](./SEGURANCA_DADOS.md). Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md).
