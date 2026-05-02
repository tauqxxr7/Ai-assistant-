# Sitemap-Aware Crawling

The crawler treats `robots.txt` as an access policy and sitemaps as discovery hints.

## Flow

1. Normalize the user-provided website or domain.
2. Fetch `https://domain/robots.txt`.
3. Extract sitemap directives from the robots file.
4. Fetch listed sitemap URLs, or fall back to `/sitemap.xml`.
5. Parse sitemap indexes and URL sets.
6. Rank URLs by query-term overlap and `lastmod`.
7. Check each candidate URL against the parsed robots rules.
8. Fetch and extract content only for allowed pages.

## Limits

`MAX_CRAWL_PAGES` limits the number of pages opened per answer. This keeps requests predictable and avoids accidentally turning one user prompt into an aggressive crawl.

## Missing Data

If robots or sitemap files are missing, the agent reports the gap. It does not invent pages or cite URLs it did not open.
