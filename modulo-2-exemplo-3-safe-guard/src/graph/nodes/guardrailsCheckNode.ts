import { PromptTemplate } from '@langchain/core/prompts';
import { OpenRouterService } from '../../services/openrouterService.ts';
import type { GraphState } from '../state.ts';
import { getUser, prompts } from '../../config.ts';

export const createGuardrailsCheckNode = (openRouterService: OpenRouterService) => {
    return async (state: GraphState): Promise<Partial<GraphState>> => {
        try {
            // LangSmith Studio: defaults when user/guardrails not in input state
            const user = state.user ?? getUser('ananeri')!;
            const guardrailsEnabled = state.guardrailsEnabled ?? false;

            const userPrompt = state.messages.at(-1)?.text!
            const template = PromptTemplate.fromTemplate(prompts.system)

            const systemPrompt = await template.format({
                USER_ROLE: user.role,
                USER_NAME: user.displayName
            })

            const msg = systemPrompt.concat('\n', userPrompt)

            const result = await openRouterService.checkGuardRails(
                msg,
                guardrailsEnabled,
            )

            return {
                user,
                guardrailsEnabled,
                guardrailCheck: result
            };
        } catch (error) {
            console.error('Guardrails check failed:', error);

            return {
                guardrailCheck: {
                    reason: 'Guardrails service unavailable - request blocked for safety',
                    safe: false,
                }
            };
        }
    }
}
