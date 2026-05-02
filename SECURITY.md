# Security Policy

## Secrets

This project does not hardcode API keys, database credentials, or deployment secrets. Use `.env` for local development and managed environment variables on Vercel, Render, or any production host.

Required keys such as `OPENAI_API_KEY`, `BRAVE_SEARCH_API_KEY`, and `TAVILY_API_KEY` must never be committed. `.env` is ignored by Git.

## Responsible Crawling

The assistant is designed to crawl conservatively:

- It checks `robots.txt` before opening sitemap-discovered pages.
- It treats robots rules as access constraints and sitemaps as discovery hints.
- It limits crawl size with `MAX_CRAWL_PAGES`.
- It reports blocked, missing, or failed pages in the verification response instead of inventing results.

Before running this publicly, add rate limiting, per-domain crawl budgets, request logging, and abuse monitoring.

## Reporting Issues

If you find a security issue, avoid posting exploit details publicly. Open a private disclosure channel with the maintainer or create a minimal GitHub issue requesting contact.
