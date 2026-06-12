import { readFileSync } from "node:fs";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { DataType, PretrainedModelOptions } from "@huggingface/transformers";

export interface TextSplitterConfig {
  chunkSize: number;
  chunkOverlap: number;
}

export interface AnswerPromptConstraints {
  language?: string;
  tone?: string;
  format?: string;
  max_length?: number;
}

/** Shape esperado de `prompts/answerPrompt.json` */
export interface AnswerPromptConfig {
  task?: string;
  role?: string;
  instructions?: string[];
  constraints?: AnswerPromptConstraints;
}

export const promptsFolder = "./prompts";

export const promptsFiles = {
  answerPrompt: `${promptsFolder}/answerPrompt.json`,
  template: `${promptsFolder}/template.txt`,
} as const;

const __dirname = dirname(fileURLToPath(import.meta.url));
const promptsDirName = promptsFolder.replace(/^\.\//, "");

export const PROMPTS_DIR = join(__dirname, "..", promptsDirName);

export const CONFIG = Object.freeze({
  neo4j: {
    url: process.env.NEO4J_URI!,
    username: process.env.NEO4J_USER!,
    password: process.env.NEO4J_PASSWORD!,
    indexName: "tensors_index",
    searchType: "vector" as const,
    textNodeProperties: ["text"],
    nodeLabel: "Chunk",
  },
  openRouter: {
    nlpModel: process.env.NLP_MODEL,
    url: "https://openrouter.ai/api/v1",
    apiKey: process.env.OPENROUTER_API_KEY,
    temperature: 0.3,
    maxRetries: 2,
    defaultHeaders: {
      "HTTP-Referer": process.env.OPENROUTER_SITE_URL,
      "X-Title": process.env.OPENROUTER_SITE_NAME,
    },
  },
  pdf: {
    path: "./tensores.pdf",
  },
  image: {
    path: "./EU.jpeg",
    personName: "Pedro Augusto de Oliveira",
    email: "pedroaugusto.gti@gmail.com",
  },
  textSplitter: {
    chunkSize: 1000,
    chunkOverlap: 200,
  },
  embedding: {
    modelName: process.env.EMBEDDING_MODEL!,
    pretrainedOptions: {
      dtype: "fp32" as DataType, // Options: 'fp32' (best quality), 'fp16' (faster), 'q8', 'q4', 'q4f16' (quantized)
    } satisfies PretrainedModelOptions,
  },
  similarity: {
    topK: 3,
  },
  promptConfig: JSON.parse(
    readFileSync(
      join(PROMPTS_DIR, basename(promptsFiles.answerPrompt)),
      "utf-8",
    ),
  ) as AnswerPromptConfig,
  templateText: readFileSync(
    join(PROMPTS_DIR, basename(promptsFiles.template)),
    "utf-8",
  ),
  output: {
    answersFolder: "./respostas",
    fileName: "resposta",
  },
});
