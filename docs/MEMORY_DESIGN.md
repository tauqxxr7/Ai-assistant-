# Memory Design

Memory is intentionally conservative. The assistant stores user preferences, recurring facts, and useful project context. It should not store secrets, credentials, health data, payment data, or other sensitive information unless the user explicitly asks for that behavior and the deployment has appropriate safeguards.

## Local Store

The local implementation uses SQLite:

- `id`
- `key`
- `value`
- `created_at`
- `updated_at`

The `MemoryStore` class isolates persistence behind a small boundary so a Postgres implementation can replace it without changing the agent.

## API Controls

- `GET /api/memories` lets users inspect memory.
- `POST /api/memories` creates an explicit memory.
- `DELETE /api/memories/{id}` removes memory.

## Production Upgrade

For multi-user production, add:

- user IDs and tenant isolation,
- encryption at rest,
- audit logs,
- semantic embeddings for retrieval,
- retention policies.
