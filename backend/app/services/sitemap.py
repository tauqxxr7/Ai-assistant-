from __future__ import annotations

import gzip
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx

from app.config import get_settings
from app.services.robots import normalize_domain


@dataclass
class SitemapUrl:
    loc: str
    lastmod: str | None = None
    priority: float | None = None


def parse_sitemap_xml(xml_text: str) -> tuple[list[SitemapUrl], list[str]]:
    root = ET.fromstring(xml_text)
    ns = {"sm": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
    if root.tag.endswith("sitemapindex"):
        sitemaps = [node.text.strip() for node in root.findall(".//sm:loc" if ns else ".//loc", ns) if node.text]
        return [], sitemaps

    urls: list[SitemapUrl] = []
    for url_node in root.findall(".//sm:url" if ns else ".//url", ns):
        loc = url_node.find("sm:loc" if ns else "loc", ns)
        if loc is None or not loc.text:
            continue
        lastmod = url_node.find("sm:lastmod" if ns else "lastmod", ns)
        priority = url_node.find("sm:priority" if ns else "priority", ns)
        urls.append(
            SitemapUrl(
                loc=loc.text.strip(),
                lastmod=lastmod.text.strip() if lastmod is not None and lastmod.text else None,
                priority=float(priority.text) if priority is not None and priority.text else None,
            )
        )
    return urls, []


async def fetch_sitemap(domain: str, candidates: list[str] | None = None, limit: int = 200) -> list[SitemapUrl]:
    settings = get_settings()
    base = normalize_domain(domain)
    sitemap_urls = candidates or [urljoin(base + "/", "sitemap.xml")]
    discovered: list[SitemapUrl] = []
    queue = list(dict.fromkeys(sitemap_urls))
    seen: set[str] = set()

    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, headers={"User-Agent": settings.user_agent}) as client:
        while queue and len(discovered) < limit:
            sitemap_url = queue.pop(0)
            if sitemap_url in seen:
                continue
            seen.add(sitemap_url)
            response = await client.get(sitemap_url, follow_redirects=True)
            response.raise_for_status()
            payload = response.content
            if sitemap_url.endswith(".gz"):
                payload = gzip.decompress(payload)
            urls, nested = parse_sitemap_xml(payload.decode("utf-8", errors="replace"))
            discovered.extend(urls)
            queue.extend(nested)

    return discovered[:limit]
