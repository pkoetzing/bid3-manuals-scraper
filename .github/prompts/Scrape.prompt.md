---
mode: agent
model: 'GPT-5 mini (Preview)'
tools: [codebase, editFiles, findTestFiles, problems, runCommands, runTasks, runTests, search, searchResults, terminalLastCommand, terminalSelection, testFailure, usages, installPythonPackage]
description: "Scrape and mirror Bid3 manuals for offline use (action-focused prompt)"
---

# Bid3 Manuals — Scraper prompt (improved)

Goal
- Mirror manuals hosted under https://bid3.afry.com/pages/ into a local
   `html/` folder so the manuals are fully navigable offline.

High-level plan (what I'll do)
- Read starting URLs from `manual_urls.json` (or `manual_sections_urls.json`).
- For each start URL, crawl only pages in the same path scope and download
   their HTML and same-site assets (CSS, JS, images, fonts).
- Rewrite internal links and asset references to local relative paths and
   save content under `html/`, preserving the online relative structure.
- Validate the local site (basic link-check) and retry or report any
   unresolved references.

Scope / constraints
- Only process URLs beginning with `https://bid3.afry.com/pages/`.
- For a start URL like
   `https://bid3.afry.com/pages/technical-manual/bid3-db-structure.html`,
   include pages under `.../technical-manual/bid3-db-structure/` and sibling
   pages in the same directory.
- Avoid crawling outside the `pages/` path and avoid external domains except
   for same-site assets when required.

Authentication
- If the site requires login, use Selenium + webdriver-manager to perform a
   real browser login using credentials from `.env` (dotenv). Extract cookies
   from the browser and populate a `requests.Session` so the crawler can make
   authenticated requests without driving the browser for every page.

Hardening (required)
- Use a configurable User-Agent and polite rate-limiting (delay per request).
- Add retries with exponential backoff for transient HTTP failures.
- Improve asset handling:
   - Download fonts and images referenced directly in HTML and within CSS
      (rewrite `url(...)` references).
   - Normalize and deduplicate assets that include query strings by hashing
      the final URL or saving query strings into filenames safely.
   - Preserve directory structure for assets and avoid name collisions.

Validation (required)
- After saving pages, run a post-scrape checker that loads each saved HTML
   file and verifies all internal `href` and resource `src` links resolve to a
   local file. Report any broken internal links and attempt a best-effort
   re-download or report them for manual review.

Deliverables
- A runnable Python module/package (no external network credentials
   committed) with:
   - `scraper` module: crawl, asset download, link rewrite, login helper.
   - `cli.py` to run the scrape against `manual_urls.json`.
   - `requirements.txt` or updated `pyproject.toml` with required libs.
   - Unit tests for key utilities and a post-scrape link-check test.
   - `README.md` with usage and troubleshooting steps.

Tools / libraries to use
- requests, beautifulsoup4, python-dotenv
- selenium, webdriver-manager (for login and cookie extraction)
- ruff, mypy for linting/type checking; pytest for tests

Run instructions (developer)
1. If necessary create and activate a venv and install deps:

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Place credentials in `.env` (example provided in `.env.example`).

3. Run the scraper:

```cmd
python -m cli manual_urls.json
```

4. Run the post-scrape checker:

```cmd
python -m tests.run_tests
```

Acceptance criteria
- All pages and same-site assets referenced from the start-URL scope are
   downloaded into `html/` and internal links point to local files.
- The post-scrape checker reports zero unresolved internal links for the
   pages in scope (or provides a short list of true failures).

Notes / follow-ups
- If login requires 2FA or other interactive steps, provide guidance or an
   alternate API/cookie source; full headless login may not be possible.
- For very large sections, consider parallelizing downloads while respecting
   rate limits and robots.txt (not implemented unless requested).

