import { test } from 'node:test';
import assert from 'node:assert/strict';
import { getCSVTOJSONTool } from '../../src/tools/csvToJSONTool.ts';

test('csv_to_json converts header and rows', async () => {
  const tool = getCSVTOJSONTool();
  const raw = await tool.invoke({
    csvText: 'id,product,price\n1,soap,5.49\n2,milk,6.99\n',
  });
  const rows = JSON.parse(raw as string);
  assert.equal(rows.length, 2);
  assert.equal(rows[0].id, '1');
  assert.equal(rows[1].product, 'milk');
});

test('csv_to_json matches e2e sales shape (string cells for Mongo $toDouble)', async () => {
  const tool = getCSVTOJSONTool();
  const csv = `id,product,price,date
1,soap,5.49,2024-01-01
2,milk,6.99,2024-01-01
3,rice,22.9,2024-01-01
`;
  const raw = await tool.invoke({ csvText: csv });
  const rows = JSON.parse(raw as string);
  assert.equal(rows.length, 3);
  assert.equal(rows[0].price, '5.49');
  assert.equal(rows[2].product, 'rice');
});

test('csv_to_json handles empty trailing newline', async () => {
  const tool = getCSVTOJSONTool();
  const raw = await tool.invoke({ csvText: 'a,b\n1,2' });
  const rows = JSON.parse(raw as string);
  assert.equal(rows.length, 1);
});
