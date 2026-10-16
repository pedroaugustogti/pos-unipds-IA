# Questões para debate — triagem de UTI

As questões estão na seção 3 do estudo de caso. Cada uma abre um pilar. Nenhuma tem resposta única no PDF.

Fonte: [`Estudo_de_Caso_Responsabilidade_IA_Atualizado.pdf`](../../materiais_aula/Estudo_de_Caso_Responsabilidade_IA_Atualizado.pdf).

## A. Justiça para uma IA (equidade)

O papel do sistema é maximizar a eficiência — o maior número absoluto de vidas, mesmo favorecendo quem já tem privilégio estrutural — ou promover equidade — acesso igual, mesmo com a taxa de sucesso da instituição menor?

Tema: eficiência médica e justiça distributiva não coincidem neste caso. “Salvar mais vidas no ano” usa a desigualdade histórica como sinal. Equidade aceita perder esse ganho estatístico para não transformar o CEP em critério de fila.

## B. Responsabilidade pelo viés (accountability)

Se o algoritmo reflete uma realidade matemática tirada de dados reais, ele está tecnicamente errado? É dever de quem desenvolve “corrigir a sociedade” alterando os pesos?

Tema: o modelo pode estar calibrado com o passado e ainda assim ser inaceitável como política de fila. Accountability não se resolve dizendo que a coluna de renda foi removida. Quem treina, quem contrata a rede pública e quem publica o modelo respondem pelo proxy que ficou (CEP e hospital de origem).

## C. Limite da transparência e da explicabilidade

A equipe implementaria o sistema sem conseguir explicar, de forma clara, à família de um paciente da periferia por que ele foi preterido? Como desenhar o termo de consentimento e a governança do hospital?

Tema: explicabilidade aqui não é mostrar o peso de uma feature. É dizer a uma família o motivo humano da preterição. Sem isso, o termo de consentimento não pode tratar a fila como neutra. Governança inclui o direito de contestar a posição, o registro da auditoria e a regra de quando o modelo sai do ar.

## O que o debate não fecha

| Pilar | Tensão que permanece |
|-------|----------------------|
| Equidade | Mais vidas no agregado contra acesso igual na mesma gravidade |
| Accountability | Dado histórico fiel contra dever de não repetir a injustiça na fila |
| Explicabilidade | Score opaco contra família que precisa de um motivo e de um canal de recurso |

Leitura do caso: [`RESPONSABILIDADE_IA.md`](./RESPONSABILIDADE_IA.md). Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md).
