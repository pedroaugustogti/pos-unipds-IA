import {
  StateGraph,
  START,
  END,
} from '@langchain/langgraph';

import { createSchedulerNode } from './nodes/schedulerNode.ts';
import { createCancellerNode } from './nodes/cancellerNode.ts';
import { createIdentifyIntentNode } from './nodes/identifyIntentNode.ts';
import { createMessageGeneratorNode } from './nodes/messageGeneratorNode.ts';
import { AppointmentStateAnnotation, type GraphState } from './state.ts';
import { OpenRouterService } from '../services/index.ts';
import { AppointmentService } from '../services/appointmentService.ts';

export type { GraphState } from './state.ts';

export function buildAppointmentGraph(
  llmClient: OpenRouterService,
  appointmentService: AppointmentService,
) {
  const workflow = new StateGraph({
    stateSchema: AppointmentStateAnnotation,
  })
    .addNode('identifyIntent', createIdentifyIntentNode(llmClient))
    .addNode('schedule', createSchedulerNode(appointmentService))
    .addNode('cancel', createCancellerNode(appointmentService))
    .addNode('message', createMessageGeneratorNode(llmClient))

    .addEdge(START, 'identifyIntent')

    .addConditionalEdges(
      'identifyIntent',
      (state: GraphState): string => {
        if (state.error || !state.intent || state.intent === 'unknown') {
          return 'message';
        }

        console.log(`➡️  Routing based on intent: ${state.intent}`);
        return state.intent;
      },
      {
        schedule: 'schedule',
        cancel: 'cancel',
        message: 'message',
      },
    )

    .addEdge('schedule', 'message')
    .addEdge('cancel', 'message')
    .addEdge('message', END);

  return workflow.compile();
}
