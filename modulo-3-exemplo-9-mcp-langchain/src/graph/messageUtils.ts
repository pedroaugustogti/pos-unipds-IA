import type { BaseMessage } from '@langchain/core/messages';

function extractMessageText(message: unknown): string | undefined {
  if (!message || typeof message !== 'object') return undefined;

  const msg = message as Record<string, unknown>;
  if (typeof msg.text === 'string' && msg.text.trim()) return msg.text;

  if (typeof msg.content === 'string' && msg.content.trim()) return msg.content;

  if (Array.isArray(msg.content)) {
    const text = msg.content
      .map((part) =>
        typeof part === 'string' ? part : (part as { text?: string })?.text ?? '',
      )
      .join('')
      .trim();
    return text || undefined;
  }

  return undefined;
}

function isHumanMessage(message: unknown): boolean {
  if (!message || typeof message !== 'object') return false;
  const msg = message as BaseMessage & { type?: string };
  const type = msg._getType?.() ?? msg.type;
  return type === 'human' || type === 'HumanMessage';
}

export function getLastHumanMessageText(messages: BaseMessage[] | undefined): string {
  const list = messages ?? [];
  const humanMessages = list.filter(isHumanMessage);
  const candidate = humanMessages.at(-1) ?? list.at(-1);
  const text = extractMessageText(candidate);

  if (!text) {
    throw new Error(
      `No user message in graph state (${list.length} message(s)). Use the Chat tab and send a prompt.`,
    );
  }

  return text;
}
