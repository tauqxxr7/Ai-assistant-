# Tool Calling

Tools are registered in `backend/app/services/tools.py` with JSON Schema 2020-12 validation and `additionalProperties: false`. This prevents the agent from passing loose or surprising arguments into infrastructure code.

## Tools

- `web_search(query)`: searches Brave or Tavily when configured.
- `open_url(url)`: fetches raw HTML for an allowed URL.
- `fetch_sitemap(domain)`: fetches `/sitemap.xml` or sitemap URLs from `robots.txt`.
- `parse_robots_txt(domain)`: fetches and parses crawler access rules.
- `extract_page_content(url)`: converts HTML to title and text.
- `save_memory(key, value)`: stores non-sensitive user-approved context.
- `retrieve_memory(query)`: retrieves matching memory records.

## Error Behavior

Tools should return actionable errors to the verification layer rather than hiding failures. A failed search or blocked page becomes part of `what_could_not_be_verified`.
