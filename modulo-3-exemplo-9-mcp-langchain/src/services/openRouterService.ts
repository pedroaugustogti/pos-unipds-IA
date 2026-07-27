import { ChatOpenAI } from '@langchain/openai';
import { config, type ModelConfig } from '../config.ts';
import { SystemMessage, HumanMessage, type AIMessage } from '@langchain/core/messages';
import type { ChatGeneration } from '@langchain/core/outputs';
import { createAgent } from 'langchain';
import { getMCPTools } from './mcpService.ts';

export class OpenRouterService {
  private readonly config: ModelConfig;
  private readonly llmClient: ChatOpenAI;
  private tools: Awaited<ReturnType<typeof getMCPTools>> = [];

  constructor(configOverride?: ModelConfig) {
    this.config = configOverride ?? config;
    this.llmClient = this.#createChatModel(this.config.models[0]);
  }

  #createChatModel(modelName: string): ChatOpenAI {
    return new ChatOpenAI({
      apiKey: this.config.apiKey,
      modelName,
      temperature: this.config.temperature,
      maxTokens: this.config.maxTokens,
      configuration: {
        baseURL: 'https://openrouter.ai/api/v1',
        defaultHeaders: {
          'HTTP-Referer': this.config.httpReferer,
          'X-Title': this.config.xTitle,
        },
      },
      modelKwargs: {
        models: this.config.models,
        provider: this.config.provider,
      },
    });
  }

  async #getTools() {
    if (!this.tools.length) {
      this.tools = await getMCPTools();
    }
    return this.tools;
  }

  async generateWithTools(systemPrompt: string, userPrompt: string): Promise<string> {
    const agent = createAgent({
      tools: await this.#getTools(),
      model: this.llmClient,
    });

    const messages = [
      new SystemMessage(systemPrompt),
      new HumanMessage(userPrompt),
    ];

    const data = await agent.invoke({ messages }, {
      recursionLimit: 100,
      callbacks: [{
        handleLLMEnd(output) {
          const msg = (output.generations?.at(0)?.at(0) as ChatGeneration)?.message as AIMessage;
          const toolCalls = msg?.tool_calls;
          if (toolCalls?.length) {
            console.log(`Tool calls: ${toolCalls.map((t) => t.name).join(', ')}`);
          }
        },
        handleToolStart(_tool, input, _runId, _parentRunId, _tags, _metadata, runName) {
          console.log(`Tool start: ${runName}`);
        },
        handleToolEnd(_output, _runId, _parentRunId, runName) {
          console.log(`Tool end: ${runName}`);
        },
      }],
    });

    return data.messages.at(-1)?.text as string ?? '';
  }
}
