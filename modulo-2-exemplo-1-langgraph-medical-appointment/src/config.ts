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
};

console.assert(process.env.OPENROUTER_API_KEY, 'OPENROUTER_API_KEY is not set in environment variables');

export const config: ModelConfig = {
  apiKey: process.env.OPENROUTER_API_KEY!,
  httpReferer: '',
  xTitle: 'IA Devs - Prompt Chaining Article Generator',
  models: [
    'nvidia/nemotron-3-nano-30b-a3b:free',
    'google/gemma-3-4b-it:free',
  ],
  provider: {
    sort: {
      by: 'throughput',
      partition: 'none',
    },
  },
  temperature: 0.7,
};
