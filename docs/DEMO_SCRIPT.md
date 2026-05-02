# Demo Script

## Demo Questions

1. "Remember that I prefer concise answers."
   - The assistant should save the preference and show it in the memory sidebar.

2. "What are the latest updates on openai.com?"
   - With API keys configured, the assistant should check website access, use sitemap/search context, stream progress, and return sources plus verification notes.
   - Without API keys configured, it should show: "Demo mode: configure API keys for live answers."

3. "What do you remember about my answer style?"
   - The assistant should retrieve local memory and mention the saved concise-answer preference.

## 60-Second Recruiter Explanation

This is a full-stack live AI assistant built as infrastructure, not a toy chatbot. The frontend is a Next.js streaming chat UI, while the FastAPI backend orchestrates memory, tool calling, web search, robots.txt checks, sitemap parsing, and page extraction. For current or website-specific questions, it decides whether to search or crawl, respects robots rules, uses sitemap URLs as discovery hints, and returns a verification contract with sources, confidence, what was verified, and what could not be verified. It also includes local memory with view/delete controls, Docker and cloud deployment config, GitHub Actions CI, and tests for the riskiest backend behavior.

## What to Point Out

- Streaming status makes agent work visible: thinking, searching, verifying.
- Missing API keys trigger demo mode instead of crashes or fake answers.
- `robots.txt` and sitemap handling show responsible internet access.
- Memory is inspectable and deletable, which is important for trust.
- The docs are honest about what is deployed and what still needs production hardening.
