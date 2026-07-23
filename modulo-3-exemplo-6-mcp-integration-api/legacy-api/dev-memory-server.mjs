import { createServer } from 'node:http';
import { randomBytes } from 'node:crypto';

const PORT = 9999;
const customers = new Map();

function objectId() {
  return randomBytes(12).toString('hex');
}

function isValidObjectId(id) {
  return /^[a-f0-9]{24}$/i.test(id);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk) => { data += chunk; });
    req.on('end', () => {
      if (!data) return resolve({});
      try {
        resolve(JSON.parse(data));
      } catch (error) {
        reject(error);
      }
    });
    req.on('error', reject);
  });
}

function send(res, status, payload) {
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  });
  res.end(JSON.stringify(payload));
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const { pathname } = url;
  const method = req.method ?? 'GET';

  if (method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
      'Access-Control-Allow-Headers': '*',
    });
    return res.end();
  }

  try {
    if (method === 'GET' && pathname === '/v1/health') {
      return send(res, 200, { app: 'customers', version: 'v1.0.1' });
    }

    if (method === 'GET' && pathname === '/v1/customers') {
      const list = [...customers.values()].sort((a, b) => a.name.localeCompare(b.name));
      return send(res, 200, list);
    }

    const customerMatch = pathname.match(/^\/v1\/customers\/([^/]+)$/);
    if (customerMatch) {
      const id = customerMatch[1];

      if (!isValidObjectId(id)) {
        return send(res, 400, { message: 'the id is invalid!', id });
      }

      if (method === 'GET') {
        const customer = customers.get(id);
        if (!customer) return send(res, 404, { error: 'User not found' });
        const { _id, ...remaining } = customer;
        return send(res, 200, { ...remaining, id });
      }

      if (method === 'PUT') {
        const body = await readBody(req);
        if (!customers.has(id)) {
          return send(res, 404, { message: 'User not found or no changes made', id });
        }
        customers.set(id, { _id: id, name: body.name, phone: body.phone });
        return send(res, 200, { message: `User ${id} updated!`, id });
      }

      if (method === 'DELETE') {
        if (!customers.delete(id)) return send(res, 404);
        return send(res, 200, { message: `User ${id} deleted!`, id });
      }
    }

    if (method === 'POST' && pathname === '/v1/customers') {
      const body = await readBody(req);
      const id = objectId();
      customers.set(id, { _id: id, name: body.name, phone: body.phone });
      return send(res, 201, { message: `user ${body.name} created!`, id });
    }

    return send(res, 404, { message: 'Not found' });
  } catch (error) {
    return send(res, 500, { message: error instanceof Error ? error.message : String(error) });
  }
});

server.listen(PORT, '::', () => {
  console.error(`[dev-memory-api] running at http://localhost:${PORT}/v1`);
});
