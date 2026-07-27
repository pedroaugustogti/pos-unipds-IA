export type ModelConfig = {
  apiKey: string;
  httpReferer: string;
  xTitle: string;
  provider: {
    sort: {
      by: string;
      partition: string;
    };
  };
  models: string[];
  temperature: number;
  maxTokens: number;
};

console.assert(process.env.OPENROUTER_API_KEY, 'OPENROUTER_API_KEY is not set in environment variables');

export const config: ModelConfig = {
  apiKey: process.env.OPENROUTER_API_KEY!,
  httpReferer: 'https://github.com/pedroaugustogti/pos-unipds-IA',
  xTitle: 'POS UNIPDS - MCP LangChain',
  models: [
    'google/gemini-2.0-flash-001',
    'openai/gpt-4o-mini',
    'meta-llama/llama-3.3-70b-instruct',
  ],
  provider: {
    sort: {
      by: 'throughput',
      partition: 'none',
    },
  },
  temperature: 0.7,
  maxTokens: 4096,
};
