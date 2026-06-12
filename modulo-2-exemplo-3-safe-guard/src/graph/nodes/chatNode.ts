import type { GraphState } from '../state.ts';
import { AIMessage } from '@langchain/core/messages';
import { OpenRouterService } from '../../services/openrouterService.ts';
import { PromptTemplate } from '@langchain/core/prompts';
import { getUser, prompts } from '../../config.ts';

export const createChatNode = (openRouterService: OpenRouterService) => {
    return async (state: GraphState): Promise<Partial<GraphState>> => {
        try {

            const user = state.user ?? getUser('ananeri')!;
            const guardrailsEnabled = state.guardrailsEnabled ?? false;

            const userPrompt = state.messages.at(-1)?.text!
            const template = PromptTemplate.fromTemplate(prompts.system)

            const systemPrompt = await template.format({
                USER_ROLE: user.role,
                USER_NAME: user.displayName
            })

            const response = await openRouterService.generate(
                systemPrompt,
                userPrompt,
            )
            return {
                messages: [new AIMessage(response)],
            };
        } catch (error) {
            console.error('Chat node error:', error);
            const status = (error as { status?: number }).status;
            const fallback =
                status === 429
                    ? 'Limite de requisições do modelo free no OpenRouter. Aguarde ~10s e tente novamente.'
                    : 'I apologize, but I encountered an error processing your request. Please try again later.';
            return {
                messages: [new AIMessage(fallback)],
            };
        }
    }
}
