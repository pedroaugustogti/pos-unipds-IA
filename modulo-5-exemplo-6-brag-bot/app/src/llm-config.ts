import { genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';
import { openAICompatible } from '@genkit-ai/compat-oai';

export type LlmProvider = 'google' | 'openrouter';

function resolveProvider(): LlmProvider {
  const explicit = process.env['LLM_PROVIDER']?.toLowerCase();
  if (explicit === 'openrouter' || explicit === 'google') {
    return explicit;
  }
  if (process.env['OPENROUTER_API_KEY']) {
    return 'openrouter';
  }
  return 'google';
}

function createGenkit() {
  const provider = resolveProvider();

  if (provider === 'openrouter') {
    const apiKey = process.env['OPENROUTER_API_KEY'];
    if (!apiKey) {
      throw new Error(
        'OPENROUTER_API_KEY ausente. Defina no .env ou use LLM_PROVIDER=google com GEMINI_API_KEY.',
      );
    }

    const modelSlug = process.env['OPENROUTER_MODEL'] ?? 'google/gemini-2.5-flash';
    const modelRef = `openrouter/${modelSlug}`;

    const ai = genkit({
      plugins: [
        openAICompatible({
          name: 'openrouter',
          apiKey,
          baseURL: process.env['OPENROUTER_BASE_URL'] ?? 'https://openrouter.ai/api/v1',
          defaultHeaders: {
            'HTTP-Referer':
              process.env['OPENROUTER_HTTP_REFERER'] ??
              'https://github.com/unipds-engenharia-de-ia-aplicada',
            'X-Title': process.env['OPENROUTER_X_TITLE'] ?? 'POS UNIPDS - BragBot',
          },
        }),
      ],
      model: modelRef,
    });

    return { ai, provider, modelRef };
  }

  const ai = genkit({
    plugins: [googleAI()],
    model: googleAI.model('gemini-2.5-flash'),
  });

  return { ai, provider, modelRef: 'googleai/gemini-2.5-flash' };
}

const llm = createGenkit();

export const ai = llm.ai;
export const llmProvider = llm.provider;
export const llmModel = llm.modelRef;
