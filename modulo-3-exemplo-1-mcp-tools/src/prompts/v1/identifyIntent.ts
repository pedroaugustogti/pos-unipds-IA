import { z } from 'zod/v3';

function inferFileType(
    fileName: string | null | undefined,
    fileContent: string | null | undefined,
): 'csv' | 'json' | 'unknown' {
    const name = (fileName ?? '').toLowerCase();
    if (name.endsWith('.csv')) return 'csv';
    if (name.endsWith('.json')) return 'json';
    const raw = (fileContent ?? '').trim();
    if (!raw) return 'unknown';
    if (raw.startsWith('{') || raw.startsWith('[')) return 'json';
    const first = raw.split('\n')[0] ?? '';
    if (first.includes(',') && /[a-zA-Z_]/.test(first)) return 'csv';
    return 'unknown';
}

const IntentSchemaRaw = z.object({
    intent: z.string().describe('A clean, concise natural-language description of what the user wants to accomplish. Do NOT include any CSV or JSON data in this field.'),
    fileContent: z.string().nullable().describe('The raw CSV or JSON block embedded in the message, exactly as provided. If there is no file content, set this to null.'),
    fileName: z.string().nullable().describe('An inferred filename or type for the data (e.g. "sales", "report"). Derive it from the question.'),
    fileType: z.enum(['csv', 'json', 'unknown']).optional().describe('The inferred file type based on the content or filename. If it looks like CSV, set to "csv". If it looks like JSON, set to "json". Otherwise, set to "unknown".'),
});

export const IntentSchema = IntentSchemaRaw.transform((d) => ({
    ...d,
    fileType: d.fileType ?? inferFileType(d.fileName, d.fileContent),
}));

export type IntentData = z.infer<typeof IntentSchema>;

export const getSystemPrompt = () =>
    `
You are an intent extraction assistant.
Analyze the user message and extract the requested fields as structured output.
The user message may contain a natural-language instruction mixed with raw file content (CSV or JSON).
Separate them cleanly: the intent is the goal, fileContent is the raw data block, fileName is the inferred file name.
If no file data is present, set fileContent and fileName to null.
Always include these JSON keys: intent, fileContent, fileName, fileType (use "csv", "json", or "unknown" for fileType).
`.trim();



