# Táticas para redução de custos

Quatro alavancas. Caching e quantização mexem no preço do token e da GPU. Routing e RAG eficiente mexem em *qual* modelo e *quanto* contexto você paga.

Leitura: `[MODELO_BASEADO_EM_API.md](./MODELO_BASEADO_EM_API.md)` · `[DILEMA_ECONOMICO_IA.md](./DILEMA_ECONOMICO_IA.md)`.

## Definições


| Tática             | Definição                                                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Prompt caching** | Guardar o estado de prefixos longos e estáveis (system prompt, política, documentos) para não reprocessar os mesmos tokens a cada request. |
| **Quantização**    | Reduzir a precisão dos pesos (ex.: FP16 → INT4) para o modelo ocupar menos memória e inferir com hardware mais barato.                     |
| **LLM routing**    | Enviar a tarefa ao modelo certo: ultraleve no trivial, caro só no complexo.                                                                |
| **RAG eficiente**  | Filtrar com rigor o que entra na janela de contexto — menos documento, menos token de entrada.                                             |




## Diferenças


| Critério        | Caching                     | Quantização            | Routing                            | RAG eficiente                      |
| --------------- | --------------------------- | ---------------------- | ---------------------------------- | ---------------------------------- |
| Onde atua       | Prefixo da chamada          | Pesos do modelo        | Escolha do modelo                  | Retrieval / rerank                 |
| O que economiza | Input repetido              | VRAM / máquina         | Calls no modelo caro               | Tokens de contexto                 |
| Quando vale     | Prefixo fixo e longo        | Serving próprio / edge | Mix de tarefas simples e difíceis  | Base grande, pergunta pontual      |
| Trade-off       | Miss, TTL, prefixo idêntico | Qualidade              | Router errado → qualidade ou custo | Recall baixo → resposta incompleta |
| Tipicamente     | OpEx API                    | CapEx/OpEx infra       | OpEx API                           | OpEx API                           |




## Características



### Prompt caching


| Traço            | Efeito                                               |
| ---------------- | ---------------------------------------------------- |
| Prefixo estático | System, política e docs fixos entram uma vez.        |
| Sufixo dinâmico  | Pergunta do usuário continua paga a cada vez.        |
| Economia         | Até ~50% na fatura quando o prefixo domina o prompt. |
| Latência         | Time to first token cai com cache hit.               |




### Quantização


| Traço           | Efeito                                                     |
| --------------- | ---------------------------------------------------------- |
| Menos bits      | FP16 → INT8/INT4 reduz VRAM de forma brusca.               |
| Hardware barato | Modelos grandes cabem em GPU de consumo ou CPU (GGUF).     |
| Formatos        | GGUF, AWQ, GPTQ, TensorRT-LLM.                             |
| Qualidade       | Eval antes de promover; tarefas sensíveis pedem mais bits. |




### LLM routing


| Traço               | Efeito                                                      |
| ------------------- | ----------------------------------------------------------- |
| Tier de modelos     | Mini/Haiku/Flash no trivial; Sonnet/Opus/GPT-4o no difícil. |
| Classificador       | Regra, embedding ou modelo leve decide a rota.              |
| Exemplo de trivial  | Filtrar e categorizar spam, triagem, extrair campo.         |
| Exemplo de complexo | Raciocínio longo, código ambíguo, negociação com risco.     |
| Economia            | A maior parte do tráfego nunca toca o modelo caro.          |




### RAG eficiente


| Traço        | Efeito                                                     |
| ------------ | ---------------------------------------------------------- |
| Top-k baixo  | Menos chunks no prompt = menos input tokens.               |
| Rerank       | Recupera muitos, manda poucos (os melhores) ao LLM.        |
| Small-to-big | Busca trecho curto; sobe o documento só se precisar.       |
| Metadados    | Filtra por repo, data, produto antes do embedding.         |
| Meta         | Cortar custo de entrada sem largar a evidência necessária. |




## Exemplos reais


| Caso                                                              | Tática                | O que mostra                                                      |
| ----------------------------------------------------------------- | --------------------- | ----------------------------------------------------------------- |
| Anthropic (prompt caching na API Claude)                          | Caching               | Prefixo (system + docs) com desconto nas leituras seguintes.      |
| OpenAI (cached input tokens)                                      | Caching               | Input repetido mais barato que o token cheio.                     |
| Google Gemini (context caching)                                   | Caching               | PDF, vídeo e system reutilizados entre requests.                  |
| llama.cpp / GGUF                                                  | Quantização           | Llama 7B–70B em INT4/Q4 no desktop.                               |
| NVIDIA TensorRT-LLM / AWQ-GPTQ no Hugging Face                    | Quantização           | Serving otimizado; pesos prontos para vLLM.                       |
| Ollama / LM Studio                                                | Quantização           | Inferência local sem fatura por token.                            |
| OpenAI (GPT-4o-mini vs GPT-4o) e Anthropic (Haiku vs Sonnet/Opus) | Routing               | Catálogo oficial de “barato vs capaz”; o produto escolhe a faixa. |
| Martian, Not Diamond, OpenRouter (model routing)                  | Routing               | Roteador externo escolhe provedor/modelo por tarefa e preço.      |
| Portkey, Helicone, LiteLLM (gateway)                              | Routing               | Proxy com fallback e regras de modelo por rota.                   |
| Cohere Rerank                                                     | RAG eficiente         | Recupera N, reordena, envia só o topo ao LLM.                     |
| Pinecone / Weaviate + metadados                                   | RAG eficiente         | Filtro por namespace/tenant antes de gastar contexto.             |
| LlamaIndex / LangChain (retrieval + rerank pipelines)             | RAG eficiente         | Padrão de mercado: retrieve amplo → rerank → prompt curto.        |
| Perplexity (busca + resposta)                                     | Routing + RAG         | Várias chamadas; sem filtro o OpEx explode por pergunta.          |
| Migração GPT-4 API → Llama quantizado                             | Quantização + routing | Volume alto justifica CapEx/serving; trivial fica no modelo leve. |




## Quando usar qual


| Situação                                       | Preferir                                    |
| ---------------------------------------------- | ------------------------------------------- |
| System prompt e docs fixos, volume alto na API | Prompt caching                              |
| Quer reduzir VRAM e rodar on-prem / edge       | Quantização                                 |
| 80% das queries são triagem/spam/classificação | LLM routing                                 |
| Base grande e o prompt inchou de chunks        | RAG eficiente (top-k + rerank)              |
| Agente com tools e prefixo estável             | Caching + routing + teto de loop            |
| Produto em escala com margem apertada          | Combinar as quatro; medir custo por request |




## Ordem prática

1. Medir onde está o token: prefixo, contexto RAG ou raciocínio.
2. Prefixo estável → caching. Contexto inchado → RAG eficiente.
3. Mix de dificuldade → routing. Serving próprio → quantização.
4. Eval de qualidade e custo por request antes de promover.

Relatório da aula: `[RELATORIO_DIDATICO_AULA.md](./RELATORIO_DIDATICO_AULA.md)`.