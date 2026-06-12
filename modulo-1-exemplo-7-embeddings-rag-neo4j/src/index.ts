import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/huggingface_transformers";
import { ChatOpenAI } from "@langchain/openai";
import { CONFIG } from "./config.ts";
import { AI } from "./ia.ts";
import { DocumentProcessor } from "./documentProcessor.ts";
import { type PretrainedOptions } from "@huggingface/transformers";
import { Neo4jVectorStore } from "@langchain/community/vectorstores/neo4j_vector";

let _neo4jVectorStore = null

async function clearAll(vectorStore: Neo4jVectorStore, nodeLabel: string): Promise<void> {
  console.log("🗑️ Removendo todos os documentos existentes...");
  await vectorStore.query(
    `MATCH (n:\`${nodeLabel}\`) DETACH DELETE n`
  )
  console.log("✅ Documentos removidos com sucesso\n");
}


try {
  console.log("🚀 Inicializando sistema de Embeddings com Neo4j...\n");

  const documentProcessor = new DocumentProcessor(
    CONFIG.pdf.path,
    CONFIG.textSplitter,
    CONFIG.image,
  )
  const pdfDocuments = await documentProcessor.loadAndSplit()
  const imageDocuments = documentProcessor.buildImageIdentityChunks()
  const documents = [...pdfDocuments, ...imageDocuments]
  console.log(`🖼️ Incluídos ${imageDocuments.length} chunks da imagem (${CONFIG.image.path})\n`)
  const embeddings = new HuggingFaceTransformersEmbeddings({
    model: CONFIG.embedding.modelName,
    pretrainedOptions: CONFIG.embedding.pretrainedOptions as PretrainedOptions
  })

  const llm = new ChatOpenAI({
    model: CONFIG.openRouter.nlpModel,
    temperature: CONFIG.openRouter.temperature,
    maxRetries: CONFIG.openRouter.maxRetries,
    configuration: {
      baseURL: CONFIG.openRouter.url,
      apiKey: CONFIG.openRouter.apiKey,
      defaultHeaders: CONFIG.openRouter.defaultHeaders,
    },
  });

  console.log('embeddings', embeddings)
  // const response = await embeddings.embedQuery(
  //   "JavaScript"
  // )
  // const response = await embeddings.embedDocuments([
  //   "JavaScript"
  // ])
  // console.log('response', response)

  _neo4jVectorStore = await Neo4jVectorStore.fromExistingGraph(
    embeddings,
    CONFIG.neo4j
  )

  clearAll(_neo4jVectorStore, CONFIG.neo4j.nodeLabel)
  for (const [index, doc] of documents.entries()) {
    console.log(`✅ Adicionando documento ${index + 1}/${documents.length}`);
    await _neo4jVectorStore.addDocuments([doc])
  }
  console.log("\n✅ Base de dados populada com sucesso!");

  // ==================== STEP 2: RUN SIMILARITY SEARCH ====================
  console.log("\n🔍 ETAPA 2: Executando buscas por similaridade...");
  const questions = [
    "O que são tensores e como são representados em JavaScript?",
    "Como converter objetos JavaScript em tensores?",
    "O que é normalização de dados e por que é necessária?",
    "Como funciona uma rede neural no TensorFlow.js?",
    "O que significa treinar uma rede neural?",
    "o que é hot enconding e quando usar?",
    "Quem aparece na foto EU.jpeg?",
    "Quem é a pessoa na imagem de perfil?",
    "Quem é essa pessoa da foto?",
  ]

  if (!_neo4jVectorStore) {
    throw new Error("Neo4j vector store não inicializado");
  }

  const ia = new AI({
    debugLog: (...args) => console.log(...args),
    vectorStore: _neo4jVectorStore,
    nlpModel: llm,
    promptConfig: CONFIG.promptConfig,
    templateText: CONFIG.templateText,
    topK: CONFIG.similarity.topK,
  });

  for (const index in questions) {
    const question = questions[index]!;

    console.log("=".repeat(80));
    console.log(`📌 PERGUNTA: ${question}`);

    const result = await ia.answerQuestion(question);
    if (result.error) {
      console.log(`❌ Erro: ${result.error}`);
      continue;
    }

    console.log(`\n${result.answer}\n`);

    await mkdir(CONFIG.output.answersFolder, { recursive: true });
    const fileName = join(
      CONFIG.output.answersFolder,
      `${CONFIG.output.fileName}-${index}-${Date.now()}.md`,
    );
    await writeFile(fileName, result.answer!, "utf-8");

    console.log("=".repeat(80));
  }

  // Cleanup
  console.log("=".repeat(80));
  console.log("✅ Processamento concluído com sucesso!\n");

} catch (error) {
  console.error('error', error)
} finally {
  await _neo4jVectorStore?.close();
}
