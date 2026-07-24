import type { ToolName } from "../../domain/authorization.ts";
import { assertToolAccess } from "../../domain/authorization.ts";
import type { TokenContext } from "../../domain/token-context.ts";

type ToolResult = {
    content: Array<{ type: "text"; text: string }>;
    structuredContent: Record<string, unknown>;
};

export async function withToolGuard<T extends ToolResult>(
    tool: ToolName,
    context: TokenContext,
    handler: () => Promise<T>
): Promise<T> {
    try {
        assertToolAccess(tool, context);
        return await handler();
    } catch (err) {
        const message = `Failed to ${tool.replace(/_/g, " ")}. Error: ${err instanceof Error ? err.message : String(err)}`;
        return {
            content: [{ type: "text", text: message }],
            structuredContent: { isError: true, message },
        } as T;
    }
}
