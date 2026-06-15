import { tool } from "@langchain/core/tools";

import csvtojson from 'csvtojson'
import { z } from 'zod/v3'

export function getCSVTOJSONTool() {
    return tool(
        async ({ csvText }) => {
            const result = await csvtojson().fromString(csvText)
            console.log('[getCSVToJSONTool] conversion result finished', result.length, 'records');

            return JSON.stringify(result)
        },
        {
            name: 'csv_to_json',
            description:
                'Convert CSV text to a JSON array of row objects (values are strings). Tool name must be exactly csv_to_json.',
            schema: z.object({
                csvText: z.string().describe('Raw CSV text including header row'),
            }),
        }
    )

}