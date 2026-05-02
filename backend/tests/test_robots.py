from app.services.robots import is_allowed


def test_robots_disallow_private_path():
    raw = """
    User-agent: *
    Disallow: /private
    Allow: /private/public
    """
    assert not is_allowed(raw, "https://example.com/robots.txt", "https://example.com/private")
    assert is_allowed(raw, "https://example.com/robots.txt", "https://example.com/private/public")


def test_robots_blocked_url_behavior():
    raw = """
    User-agent: *
    Disallow: /admin
    """
    assert not is_allowed(raw, "https://example.com/robots.txt", "https://example.com/admin/settings")
    assert is_allowed(raw, "https://example.com/robots.txt", "https://example.com/docs")
