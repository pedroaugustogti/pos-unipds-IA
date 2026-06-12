import { type Neo4jVectorStore } from "@langchain/community/vectorstores/neo4j_vector";
import { ChatOpenAI } from "@langchain/openai";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { RunnableSequence } from "@langchain/core/runnables";
import type { AnswerPromptConfig } from "./config.ts";

type DebugLog = (...args: unknown[]) => void;

type params = {
  debugLog: DebugLog;
  vectorStore: Neo4jVectorStore;
  nlpModel: ChatOpenAI;
  promptConfig: AnswerPromptConfig;
  templateText: string;
  topK: number;
};

export interface ChainState {
  question: string;
  context?: string;
  topScore?: number;
  error?: string;
  answer?: string;
}

export type AnswerResult = { answer: string; error?: undefined } | { error: string; answer?: undefined };

function normalizeRoleForTemplate(role: string): string {
  const prefix = "Você é um ";
  return role.startsWith(prefix) ? role.slice(prefix.length) : role;
}

export class AI {
  private params: params;

  constructor(params: params) {
    this.params = params;
  }

  async retrieveVectorSearchResults(input: ChainState): Promise<ChainState> {
    const { debugLog, vectorStore, topK } = this.params;
    debugLog("🔍 Buscando no vector store do Neo4j...");

    const vectorResults = await vectorStore.similaritySearchWithScore(
      input.question,
      topK,
    );

    if (!vectorResults.length) {
      debugLog("⚠️ Nenhum resultado encontrado no vector store.");
      return {
        ...input,
        error:
          "Desculpe, não encontrei informações relevantes sobre essa pergunta na base de conhecimento.",
      };
    }

    const filtered = vectorResults.filter(([, score]) => Number(score) > 0.5);

    if (!filtered.length) {
      debugLog("⚠️ Nenhum resultado acima do limiar de similaridade (0.5).");
      return {
        ...input,
        error:
          "Desculpe, não encontrei informações relevantes sobre essa pergunta na base de conhecimento.",
      };
    }

    const contexts = filtered
      .map(([doc]) => doc.pageContent)
      .join("\n\n---\n\n");

    const topScore = Number(filtered[0]![1]);
    debugLog(
      `✅ Encontrados ${filtered.length} resultados relevantes (melhor score: ${topScore.toFixed(3)})`,
    );

    const retrieved: ChainState = {
      ...input,
      error: undefined,
      context: contexts,
      topScore,
    };
    debugLog("📦 Retorno retrieveVectorSearchResults:", retrieved);

    return retrieved;
  }

  async generateNLPResponse(input: ChainState): Promise<ChainState> {
    if (input.error) {
      return input;
    }

    this.params.debugLog("🤖 Gerando resposta com IA...");

    const { nlpModel, templateText, promptConfig } = this.params;
    const c = promptConfig.constraints ?? {};

    const instructions =
      Array.isArray(promptConfig.instructions) && promptConfig.instructions.length > 0
        ? promptConfig.instructions
            .map((instruction: string, idx: number) => `${idx + 1}. ${instruction}`)
            .join("\n")
        : "";

    const responsePrompt = ChatPromptTemplate.fromTemplate(templateText);

    const responseChain = responsePrompt
      .pipe(nlpModel)
      .pipe(new StringOutputParser());

    const rawResponse = await responseChain.invoke({
      role: normalizeRoleForTemplate(promptConfig.role ?? "assistente"),
      task: promptConfig.task ?? "",
      tone: c.tone ?? "",
      language: c.language ?? "",
      format: c.format ?? "",
      instructions,
      question: input.question,
      context: input.context ?? "",
    });

    console.log('rawResponse', rawResponse)

    return {
      ...input,
      answer: rawResponse,
    };
  }

  async answerQuestion(question: string): Promise<AnswerResult> {
    const state: ChainState = { question };

    try {
      const chain = RunnableSequence.from([
        this.retrieveVectorSearchResults.bind(this),
        this.generateNLPResponse.bind(this),
      ]);

      const finalState = await chain.invoke(state);

      if (finalState.error && !finalState.answer) {
        return { error: finalState.error };
      }
      if (!finalState.answer) {
        return { error: "O modelo não retornou resposta." };
      }
      return { answer: finalState.answer };
    } catch (err) {
      return {
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }
}
