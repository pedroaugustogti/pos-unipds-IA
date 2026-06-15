import { AIMessage } from "@langchain/core/messages";
import { createMiddleware } from "langchain";

/** Poolside / multi-channel models sometimes append `<|channel|>…` to `tool_calls[].name`. */
function stripToolChannelSuffix(name: string): string {
  const i = name.indexOf("<|");
  return i === -1 ? name : name.slice(0, i);
}

export const sanitizeToolCallNamesMiddleware = createMiddleware({
  name: "SanitizeToolCallNames",
  wrapModelCall: async (request, handler) => {
    const response = await handler(request);
    if (!AIMessage.isInstance(response)) return response;
    const calls = response.tool_calls;
    if (!calls?.length) return response;
    const next = calls.map((tc) => ({
      ...tc,
      name:
        typeof tc.name === "string" ? stripToolChannelSuffix(tc.name) : tc.name,
    }));
    const same =
      next.length === calls.length &&
      next.every((t, i) => t.name === calls[i].name);
    if (same) return response;
    return new AIMessage({
      content: response.content,
      additional_kwargs: response.additional_kwargs,
      response_metadata: response.response_metadata,
      id: response.id,
      name: response.name,
      tool_calls: next,
    });
  },
});
