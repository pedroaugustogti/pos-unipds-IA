# Tipos de regulação

Dois modos de o regulador falar com quem desenvolve IA. Soft law aponta o valor. Hard law fixa a obrigação e a pena.

Leitura da aula: [`SEGURANCA_DADOS.md`](./SEGURANCA_DADOS.md). Caso de triagem: [`QUESTOES_PARA_DEBATE.md`](../../../modulo-10-exemplo-1-aspectos-humanos-eticos/docs/exemplo_aula/QUESTOES_PARA_DEBATE.md).

| Tipo | O que o regulador faz | O que não faz |
|------|------------------------|---------------|
| Princípios (soft law, flexível) | Publica diretrizes éticas, valores e objetivos. Quem desenvolve escolhe o meio. | Não descreve o controle técnico nem aplica multa por si. |
| Regras (hard law, rígida) | Impõe obrigação legal, limite e sanção. | Não deixa o cumprimento só na boa vontade. |

## Soft law — exemplos reais

| Instrumento | O que pede | Por que é flexível |
|-------------|------------|--------------------|
| Princípios de IA da OCDE (2019) | Crescimento inclusivo, valores centrados na pessoa, transparência, robustez e responsabilização. O Brasil aderiu. | Não há multa. O texto orienta política pública e contrato. |
| Recomendação da UNESCO sobre a ética da IA (2021) | Proporcionalidade, segurança, equidade, transparência e supervisão humana. | Recomendação. O Estado traduz se quiser. |
| AI Risk Management Framework do NIST (2023) | Mapear, medir, gerir e governar risco de IA. | Voluntário nos Estados Unidos. Vira exigência só quando um contrato ou um edital o cita. |
| Diretrizes do grupo de especialistas da Comissão Europeia para uma IA confiável (2019) | Sete requisitos: agência humana, robustez, privacidade, transparência, equidade, bem-estar e responsabilização. | Vieram antes do AI Act. Não sancionam. |

No caso da fila de UTI, soft law diz para não transformar desigualdade histórica em critério e para explicar a decisão à família. Não diz qual variável tirar, nem quanto custa descumprir.

## Hard law — exemplos reais

| Instrumento | Obrigação | Sanção |
|-------------|-----------|--------|
| Regulamento europeu de IA (Regulamento (UE) 2024/1689), em vigor em 1º de agosto de 2024 | Proíbe práticas (pontuação social, parte do reconhecimento biométrico em tempo real). Sistema de alto risco — inclusive priorização de atendimento de emergência e acesso a serviço público essencial — exige gestão de risco, dados, registro, transparência e supervisão humana. | Até 35 milhões de euros ou 7% do faturamento mundial anual nas práticas proibidas. Até 15 milhões ou 3% nas outras obrigações. |
| LGPD (Lei 13.709/2018) | Base legal, necessidade, segurança e direitos do titular. Dado de saúde da fila de UTI é dado pessoal sensível. Decisão automatizada dá ao titular o direito de pedir revisão por pessoa natural. | Advertência e multa de até 2% do faturamento no Brasil, limitada a R$ 50 milhões por infração. |
| GDPR, artigo 22 | A pessoa pode não ficar sujeita a decisão só automatizada que produza efeito jurídico ou equivalente. Saúde e acesso a cuidado entram nesse efeito. | Até 20 milhões de euros ou 4% do faturamento global. |

A mesma fila, sob hard law, precisa de base legal, revisão humana, registro da auditoria e um responsável que a autoridade possa multar. Tirar a coluna de renda e deixar o CEP não encerra o dever.

## O que esta aula já cobre

| Tipo | Onde aparece aqui |
|------|-------------------|
| Soft law | A regra “cliente bloqueado não recebe vantagem” escrita só na `system_instruction` do notebook. Orienta o modelo. Não impede o histórico de tentar anulá-la. |
| Hard law | O controle em [`02-demonstracao`](../exemplo_real/02-demonstracao/README.md): o histórico não autoriza cupom. Num hospital, o equivalente é a obrigação de a política vencer o dado, com alguém responsável se ela falhar. |
| Os dois juntos | OWASP nomeia o risco ([`OWASP_TOP10_LLM.md`](./OWASP_TOP10_LLM.md)). Soft law diz para tratar o risco. Hard law exige o controle e cobra a falha. O caso Air Canada (2024) é hard law na prática: o chatbot inventou uma tarifa e o tribunal manteve a empresa. |

Relatório da aula: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md).
