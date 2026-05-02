from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

from app.config import get_settings


@dataclass
class RobotsInfo:
    domain: str
    robots_url: str
    allowed_root: bool
    sitemaps: list[str]
    raw: str
    error: str | None = None


def normalize_domain(domain: str) -> str:
    domain = domain.strip()
    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"
    return domain.rstrip("/")


async def parse_robots_txt(domain: str) -> RobotsInfo:
    settings = get_settings()
    base = normalize_domain(domain)
    robots_url = urljoin(base + "/", "robots.txt")
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, headers={"User-Agent": settings.user_agent}) as client:
            response = await client.get(robots_url, follow_redirects=True)
            response.raise_for_status()
        raw = response.text
    except Exception as exc:  # noqa: BLE001 - returned to the verification engine.
        return RobotsInfo(domain=base, robots_url=robots_url, allowed_root=False, sitemaps=[], raw="", error=str(exc))

    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(raw.splitlines())
    sitemaps = [line.split(":", 1)[1].strip() for line in raw.splitlines() if line.lower().startswith("sitemap:")]
    return RobotsInfo(
        domain=base,
        robots_url=robots_url,
        allowed_root=parser.can_fetch(settings.user_agent, base + "/"),
        sitemaps=sitemaps,
        raw=raw,
    )


def is_allowed(robots_raw: str, robots_url: str, url: str) -> bool:
    explicit = _allowed_by_longest_rule(robots_raw, url)
    if explicit is not None:
        return explicit
    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.parse(robots_raw.splitlines())
    return parser.can_fetch(get_settings().user_agent, url)


def _allowed_by_longest_rule(robots_raw: str, url: str) -> bool | None:
    path = urlparse(url).path or "/"
    groups: list[tuple[list[str], list[tuple[str, str]]]] = []
    agents: list[str] = []
    rules: list[tuple[str, str]] = []

    def flush() -> None:
        nonlocal agents, rules
        if agents:
            groups.append((agents, rules))
        agents = []
        rules = []

    for raw_line in robots_raw.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = [part.strip() for part in line.split(":", 1)]
        key = key.lower()
        if key == "user-agent":
            if rules:
                flush()
            agents.append(value.lower())
        elif key in {"allow", "disallow"} and agents:
            rules.append((key, value))

    flush()
    candidates = [rules for agents, rules in groups if "*" in agents]
    if not candidates:
        return None

    matches: list[tuple[int, bool]] = []
    for group_rules in candidates:
        for directive, pattern in group_rules:
            if pattern == "":
                continue
            if path.startswith(pattern):
                matches.append((len(pattern), directive == "allow"))
    if not matches:
        return True
    return sorted(matches, key=lambda item: item[0], reverse=True)[0][1]
