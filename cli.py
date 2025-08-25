"""Small CLI entrypoint to run the scraper."""
from __future__ import annotations

import sys
from pathlib import Path

from src import scraper


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv) if argv is None else argv
    src = Path(argv[1]) if len(argv) > 1 else Path.cwd() / "manual_urls.json"
    n = scraper.scrape_from(src)
    print(f"Saved {n} pages to {scraper.HTML_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
