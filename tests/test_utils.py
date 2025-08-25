from src import scraper


def test_sanitize_local_path():
    url = "https://bid3.afry.com/pages/technical-manual/bid3-db-structure.html"
    p = scraper.sanitize_local_path(url)
    assert "technical-manual" in str(p)
    assert p.suffix == ".html"


def test_allowed_scope():
    assert scraper.allowed_scope("https://bid3.afry.com/pages/foo.html")
    assert not scraper.allowed_scope("https://example.com/pages/foo.html")
