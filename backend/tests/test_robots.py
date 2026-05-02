from app.services.robots import is_allowed


def test_robots_disallow_private_path():
    raw = """
    User-agent: *
    Disallow: /private
    Allow: /private/public
    """
    assert not is_allowed(raw, "https://example.com/robots.txt", "https://example.com/private")
    assert is_allowed(raw, "https://example.com/robots.txt", "https://example.com/private/public")
