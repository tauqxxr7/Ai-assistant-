# Architecture

The assistant is split into two deployable services:

- `frontend/`: Next.js, TypeScript, Tailwind CSS, shadcn-style primitives, and SSE stream handling.
- `backend/`: FastAPI agent API, crawling tools, search adapters, verification contract, and memory.

The backend owns all privileged work: LLM calls, web search, sitemap crawling, memory, and verification. The frontend only renders state and streams.

## Runtime Path

1. The user sends a message to `POST /api/chat`.
2. `AgentOrchestrator` retrieves relevant memory.
3. The agent checks for current-data signals such as "latest" or a domain.
4. If a domain is present, the agent checks `robots.txt`, parses sitemap URLs, ranks relevant pages, and opens allowed URLs.
5. If no domain pages are available and the question needs current data, the agent calls the configured search provider.
6. The LLM receives only the question, memory, source text, and verification notes.
7. The final response is streamed as SSE with tokens and a structured final payload.

## Production Notes

- Keep API keys in managed environment variables.
- Put the backend behind rate limiting before public launch.
- Replace local SQLite with a Postgres adapter for multi-user production.
- Add crawl budgets and domain-level caching before high-volume crawling.
