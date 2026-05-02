from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

from app.config import get_settings
from app.services.robots import is_allowed, parse_robots_txt
from app.services.sitemap import SitemapUrl, fetch_sitemap


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip = False
        self.title: str | None = None
        self._in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip = True
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str):
        if tag in {"script", "style", "noscript"}:
            self.skip = False
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str):
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title = text
        if not self.skip:
            self.parts.append(text)


@dataclass
class PageContent:
    url: str
    title: str | None
    text: str


def domain_from_url(url: str) -> str:
    parsed = urlparse(url if url.startswith(("http://", "https://")) else f"https://{url}")
    return f"{parsed.scheme}://{parsed.netloc}"


async def open_url(url: str) -> str:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, headers={"User-Agent": settings.user_agent}) as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        return response.text


async def extract_page_content(url: str) -> PageContent:
    html = await open_url(url)
    parser = TextExtractor()
    parser.feed(html)
    text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    return PageContent(url=url, title=parser.title, text=text[:12000])


def rank_sitemap_urls(urls: list[SitemapUrl], query: str, limit: int) -> list[SitemapUrl]:
    terms = [term.lower() for term in re.findall(r"[a-zA-Z0-9]{3,}", query)]

    def score(item: SitemapUrl) -> tuple[int, str]:
        loc = item.loc.lower()
        term_score = sum(1 for term in terms if term in loc)
        recency = item.lastmod or ""
        return (term_score, recency)

    return sorted(urls, key=score, reverse=True)[:limit]


async def sitemap_aware_pages(domain: str, query: str) -> tuple[list[PageContent], list[str], list[str]]:
    settings = get_settings()
    verified: list[str] = []
    missing: list[str] = []
    robots = await parse_robots_txt(domain)
    if robots.error:
        missing.append(f"robots.txt could not be fetched: {robots.error}")
        return [], verified, missing
    verified.append(f"robots.txt checked at {robots.robots_url}")

    try:
        sitemap_urls = await fetch_sitemap(domain, robots.sitemaps or None)
        verified.append(f"sitemap parsed with {len(sitemap_urls)} discovered URLs")
    except Exception as exc:  # noqa: BLE001
        missing.append(f"sitemap could not be parsed: {exc}")
        sitemap_urls = []

    pages: list[PageContent] = []
    for item in rank_sitemap_urls(sitemap_urls, query, settings.max_crawl_pages):
        if not is_allowed(robots.raw, robots.robots_url, item.loc):
            missing.append(f"robots.txt disallowed {item.loc}")
            continue
        try:
            pages.append(await extract_page_content(item.loc))
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{item.loc} could not be opened: {exc}")
    return pages, verified, missing
