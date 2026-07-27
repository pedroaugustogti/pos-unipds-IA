import { createServer } from './server.ts';

const port = Number(process.env.PORT ?? 3009);
const app = await createServer();

await app.listen({ port, host: '0.0.0.0' });
console.log(`Server running on http://127.0.0.1:${port}`);
