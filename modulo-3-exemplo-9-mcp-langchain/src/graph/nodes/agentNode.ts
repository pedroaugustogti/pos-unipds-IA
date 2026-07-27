import { AIMessage } from '@langchain/core/messages';
import { getSystemPrompt } from '../../prompts/v1/agentNode.ts';
import { OpenRouterService } from '../../services/openRouterService.ts';
import { getLastHumanMessageText } from '../messageUtils.ts';
import type { GraphState } from '../state.ts';

export function agentNode(openRouterService: OpenRouterService) {
  return async (state: GraphState): Promise<Partial<GraphState>> => {
    console.log('Agent node processing...');
    try {
      const rawQuestion = getLastHumanMessageText(state.messages);
      const systemPrompt = getSystemPrompt();
      const answer = await openRouterService.generateWithTools(systemPrompt, rawQuestion);

      return {
        answer,
        error: undefined,
        messages: [new AIMessage(answer)],
      };
    } catch (error) {
      console.error('Agent node error:', error);
      return {
        messages: [new AIMessage('Sorry, an error occurred while processing your request.')],
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  };
}
