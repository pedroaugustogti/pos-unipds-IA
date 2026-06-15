import { ChatOpenAI } from '@langchain/openai';
import { config, type ModelConfig } from '../config.ts';
import { SystemMessage, HumanMessage, AIMessage } from '@langchain/core/messages';
import { createAgent } from 'langchain';
import { sanitizeToolCallNamesMiddleware } from './sanitizeToolCallNamesMiddleware.ts';
import { getMCPTools } from './mcpService.ts';
import { z } from 'zod/v3';
import { type ChatGeneration } from '@langchain/core/outputs';

function messageTextContent(msg: AIMessage): string {
    const c = msg.content;
    if (typeof c === 'string') return c;
    if (Array.isArray(c)) {
        return c
            .map((part) =>
                typeof part === 'string'
                    ? part
                    : part && typeof part === 'object' && 'text' in part
                      ? String((part as { text?: string }).text)
                      : '',
            )
            .join('');
    }
    return String(c ?? '');
}

/** Free models often wrap JSON in ``` fences. */
function extractJsonObject(raw: string): unknown {
    let t = raw.trim();
    const fenced = /^```(?:json)?\s*([\s\S]*?)```$/im.exec(t);
    if (fenced) t = fenced[1].trim();
    const first = t.indexOf('{');
    const last = t.lastIndexOf('}');
    if (first === -1 || last < first) {
        throw new SyntaxError('No JSON object in model output');
    }
    return JSON.parse(t.slice(first, last + 1));
}

export class OpenRouterService {
    private config: ModelConfig;
    private llmClient: ChatOpenAI;
    private tools: any[];

    constructor(configOverride?: ModelConfig) {
        this.config = configOverride ?? config;
        this.llmClient = this.#createChatModel(this.config.models[0]);
        this.tools = [];
    }

    #createChatModel(modelName: string, temperature?: number): ChatOpenAI {
        return new ChatOpenAI({
            apiKey: this.config.apiKey,
            modelName: modelName,
            temperature: temperature ?? this.config.temperature,
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

    async generateStructured<T>(
        systemPrompt: string,
        userPrompt: string,
        schema?: z.ZodSchema<T>,
    ): Promise<{ data?: T | string; }> {
        const messages = [
            new SystemMessage(systemPrompt),
            new HumanMessage(userPrompt),
        ];

        if (schema) {
            const structuredLlm = this.#createChatModel(this.config.models[0]);
            const jsonSystem = new SystemMessage(
                `${systemPrompt}\n\nReply with exactly one JSON object only. Do not use markdown code fences. Use null where a field is unknown. Include keys: intent, fileContent, fileName, fileType.`,
            );
            const response = await structuredLlm.invoke(
                [jsonSystem, new HumanMessage(userPrompt)],
                {
                    callbacks: [{
                        handleChatModelStart(_llm, promptMessages) {
                            const lastMsg = promptMessages.at(-1)?.at(-1);
                            console.log(`\n🧠 LLM thinking...`);
                            console.log(` (last message: "${lastMsg?.content?.toString()}")`);
                        },
                    }],
                },
            );
            const text = messageTextContent(response as AIMessage);
            let parsed: T;
            try {
                parsed = schema.parse(extractJsonObject(text)) as T;
            } catch (e) {
                const preview = text.length > 800 ? `${text.slice(0, 800)}…` : text;
                throw new Error(
                    `Structured parse failed: ${e instanceof Error ? e.message : e}. Raw: ${preview}`,
                );
            }
            console.log('✅ LLM structured response:', JSON.stringify(parsed, null, 2));
            return { data: parsed };
        }

        const agent = createAgent({
            tools: await this.#getTools(),
            model: this.llmClient,
            middleware: [sanitizeToolCallNamesMiddleware],
        });

        const data = await agent.invoke(
            {
                messages
            },
            {
                callbacks: [{
                    handleChatModelStart(_llm, promptMessages) {
                        const lastMsg = promptMessages.at(-1)?.at(-1);
                        console.log(`\n🧠 LLM thinking...`);
                        console.log(` (last message: "${lastMsg?.content?.toString()}")`);
                    },
                    handleLLMEnd(output) {
                        const msg = (output.generations?.at(0)?.at(0) as ChatGeneration)?.message as AIMessage;
                        const toolCalls = msg?.tool_calls;
                        if (toolCalls?.length) {
                            console.log(`🎯 Decided to call: ${toolCalls.map((t) => t.name).join(', ')}`);
                        }
                    },
                    handleToolStart(_tool, input, _runId, _parentRunId, _tags, _metadata, runName) {
                        console.log(`🔧 Tool called: ${runName} →`, input);
                    },
                    handleToolEnd(output, _runId, _parentRunId, runName) {
                        console.log(`✅ Tool done:   ${runName} →`, output);
                    },
                }]
            });
        console.log('✅ LLM Response:', JSON.stringify(data, null, 2));

        return {
            data: data.messages.at(-1)?.text as string ?? "",
        };
    }
}
