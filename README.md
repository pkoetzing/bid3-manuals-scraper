# Bid3 Manuals Scraper

Small scraper to mirror Bid3 manuals under `https://bid3.afry.com/pages/` into
the local `html/` folder.

Usage (from repo root):

    python -m cli manual_urls.json

The project uses `requests` and `beautifulsoup4` for HTML fetching and rewriting.
