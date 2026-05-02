from app.services.sitemap import parse_sitemap_xml


def test_parse_urlset_sitemap():
    xml = """<?xml version="1.0"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>https://example.com/blog/latest</loc><lastmod>2026-05-01</lastmod><priority>0.8</priority></url>
    </urlset>"""
    urls, nested = parse_sitemap_xml(xml)
    assert nested == []
    assert urls[0].loc == "https://example.com/blog/latest"
    assert urls[0].lastmod == "2026-05-01"
    assert urls[0].priority == 0.8


def test_parse_sitemap_index():
    xml = """<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <sitemap><loc>https://example.com/post-sitemap.xml</loc></sitemap>
    </sitemapindex>"""
    urls, nested = parse_sitemap_xml(xml)
    assert urls == []
    assert nested == ["https://example.com/post-sitemap.xml"]


def test_parse_multiple_sitemaps_from_index():
    xml = """<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <sitemap><loc>https://example.com/pages.xml</loc></sitemap>
      <sitemap><loc>https://example.com/blog.xml</loc></sitemap>
    </sitemapindex>"""
    urls, nested = parse_sitemap_xml(xml)
    assert urls == []
    assert nested == ["https://example.com/pages.xml", "https://example.com/blog.xml"]
