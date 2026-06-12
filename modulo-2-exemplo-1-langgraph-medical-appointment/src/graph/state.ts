import { MessagesZodMeta } from '@langchain/langgraph';
import { withLangGraph } from '@langchain/langgraph/zod';
import type { BaseMessage } from '@langchain/core/messages';
import { z } from 'zod/v3';

export const AppointmentStateAnnotation = z.object({
  messages: withLangGraph(
    z.custom<BaseMessage[]>(),
    MessagesZodMeta,
  ),

  patientName: z.string().optional(),

  intent: z.enum(['schedule', 'cancel', 'unknown']).optional(),
  professionalId: z.number().optional(),
  professionalName: z.string().optional(),
  datetime: z.string().optional(),
  reason: z.string().optional(),

  actionSuccess: z.boolean().optional(),
  actionError: z.string().optional(),
  appointmentData: z.any().optional(),

  error: z.string().optional(),
});

export type GraphState = z.infer<typeof AppointmentStateAnnotation>;
