"""Crawler utilities for mirroring pages from bid3.afry.com under /pages/.

Features implemented:
- Load starting URLs from a JSON file (see `manual_urls.json`).
- Crawl pages within the same directory scope for each start URL.
- Download same-site assets (css/js/img) used by pages.
- Rewrite internal links to local relative paths and save under `html/`.

Note: Authentication via Selenium can be implemented but is optional. If the
site requires login you can provide cookies in a requests.Session prior to
calling the crawler.
"""
from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
# use modern union types (X | None) where needed

import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urlparse, urlsplit, urlunsplit
import hashlib
import mimetypes
import logging

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:
    webdriver = None  # selenium optional


BASE_PATH = Path(__file__).resolve().parents[1]
HTML_DIR = BASE_PATH / "html"
DOMAIN = "https://bid3.afry.com"
PAGES_PREFIX = DOMAIN + "/pages/"


def load_start_urls(manuals_json: Path) -> Iterable[str]:
    """Load starting URLs from the provided JSON file.

    Supports two shapes: a top-level {"urls": [...]} or an object containing
    lists (like `manual_sections_urls.json`) which will be flattened.
    """
    if not manuals_json.exists():
        raise FileNotFoundError(manuals_json)
    data = json.loads(manuals_json.read_text(encoding="utf8"))
    if isinstance(data, dict) and "urls" in data:
        return data["urls"]
    urls: list[str] = []
    for v in data.values():
        if isinstance(v, list):
            urls.extend(v)
    return urls


def allowed_scope(url: str) -> bool:
    return url.startswith(PAGES_PREFIX)


def sanitize_local_path(url: str) -> Path:
    """Map a full URL to a local `html/` path preserving structure."""
    if not allowed_scope(url):
        raise ValueError(f"URL outside allowed scope: {url}")
    rel = re.sub(r"^https?://[^/]+/pages/", "", url)
    return HTML_DIR / rel


def _make_session_with_cookies(cookies: dict | None = None) -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    })
    if cookies:
        jar = requests.cookies.RequestsCookieJar()
        for k, v in cookies.items():
            jar.set(k, v, domain="bid3.afry.com")
        s.cookies = jar
    return s


def download_resource(session: requests.Session, url: str, dest: Path) -> None:
    """Download a resource and save to dest. Creates parent dirs."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    # simple retry
    for attempt in range(3):
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            dest.write_bytes(resp.content)
            return
        sleep(0.5 * (attempt + 1))
    resp.raise_for_status()


def _abs_url(base: str, link: str) -> str | None:
    if not link:
        return None
    if link.startswith("http://") or link.startswith("https://"):
        return link
    if link.startswith("//"):
        return "https:" + link
    # relative URLs
    if link.startswith("/"):
        return DOMAIN + link
    # relative to base
    if base.endswith("/"):
        return base + link
    return base.rsplit("/", 1)[0] + "/" + link


def _local_for_url(url: str) -> Path:
    """Return a local path for a URL under HTML_DIR, handling query strings.

    If a query string exists, append a hash suffix to avoid duplicates.
    """
    parsed = urlsplit(url)
    rel = re.sub(r"^https?://[^/]+/", "", url)
    base = HTML_DIR / rel
    if parsed.query:
        # add a short hash to filename
        stem = base.stem
        h = hashlib.sha1(parsed.query.encode("utf8")).hexdigest()[:8]
        new_name = f"{stem}-{h}{base.suffix}"
        base = base.with_name(new_name)
    return base


def rewrite_links_and_save(
    session: requests.Session, url: str, html: str
) -> None:
    """Rewrite internal /pages/ links to local paths, download assets, and
    save HTML.
    """
    soup = BeautifulSoup(html, "html.parser")

    # attributes to inspect and whether they are resources to download
    attr_tags = [
        ("a", "href", False),
        ("link", "href", True),
        ("script", "src", True),
        ("img", "src", True),
    ]

    for tag, attr, is_asset in attr_tags:
        for node in soup.find_all(tag):
            if not node.has_attr(attr):
                continue
            val = node.get(attr)
            if not isinstance(val, str):
                continue
            abs_u = _abs_url(url, val)
            if not abs_u:
                continue
            if abs_u.startswith(PAGES_PREFIX):
                # map to local relative path within html/
                local = re.sub(r"^https?://[^/]+/pages/", "", abs_u)
                node[attr] = "./" + local
            elif is_asset and abs_u.startswith(DOMAIN):
                # download same-site asset and point to local path
                # handle inline css url(...) later; here download common assets
                dest = _local_for_url(abs_u)
                try:
                    download_resource(session, abs_u, dest)
                except Exception:
                    logging.warning("failed to download %s", abs_u)
                    continue
                # set relative path
                rel = dest.relative_to(HTML_DIR)
                node[attr] = "./" + str(rel).replace("\\", "/")

    # rewrite inline CSS url(...) patterns and download those assets
    for style_tag in soup.find_all("style"):
        text = style_tag.string
        if not text:
            continue
        def repl(m):
            url = m.group(1).strip('"\'')
            abs_u = _abs_url(base=url, link=url) if url else None
            if abs_u and abs_u.startswith(DOMAIN):
                dest = _local_for_url(abs_u)
                try:
                    download_resource(session, abs_u, dest)
                except Exception:
                    return m.group(0)
                rel = dest.relative_to(HTML_DIR)
                return f"url(./{rel})"
            return m.group(0)
        new_text = re.sub(r"url\(([^)]+)\)", repl, text)
        style_tag.string.replace_with(new_text)

    out_path = sanitize_local_path(url)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(str(soup), encoding="utf8")


def crawl_directory(start_url: str, session: requests.Session | None = None) -> int:
    """Crawl and download all pages under the directory scope for start_url.

    For a start URL ending with `name.html` we additionally include pages
    under `.../name/` as requested in the spec.
    Returns number of pages saved.
    """
    if session is None:
        session = _make_session_with_cookies()
    if not allowed_scope(start_url):
        return 0

    # directory prefixes to include
    prefixes = set()
    base_dir = start_url.rsplit("/", 1)[0] + "/"
    prefixes.add(base_dir)
    if start_url.endswith(".html"):
        base, name = start_url.rsplit("/", 1)
        alt = f"{base}/{name.replace('.html', '')}/"
        prefixes.add(alt)

    to_visit = [start_url]
    seen = set()
    saved = 0
    while to_visit:
        u = to_visit.pop(0)
        if u in seen:
            continue
        seen.add(u)
        try:
            resp = session.get(u)
            resp.raise_for_status()
        except Exception:
            continue
        html = resp.text
        rewrite_links_and_save(session, u, html)
        saved += 1

        # find links to other pages within prefixes
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a"):
            href = a.get("href")
            abs_u = _abs_url(u, href) if isinstance(href, str) else None
            if not abs_u or not allowed_scope(abs_u):
                continue
            if any(abs_u.startswith(p) for p in prefixes):
                if abs_u not in seen:
                    to_visit.append(abs_u)

    return saved


def scrape_from(manuals_json: Path) -> int:
    """Scrape starting URLs from the given JSON file. Returns number of pages saved."""
    session = _make_session_with_cookies()
    total = 0
    for url in load_start_urls(manuals_json):
        if not allowed_scope(url):
            continue
        print(f"Crawling: {url}")
        total += crawl_directory(url, session=session)
    return total


if __name__ == "__main__":
    import sys

    src = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "manual_urls.json"
    )
    n = scrape_from(src)
    print(f"Saved {n} pages to {HTML_DIR}")


def selenium_login_and_cookies(login_url: str, username: str, password: str, headless: bool = True) -> dict:
    """Use selenium to log in and return a dict of cookies usable by requests.

    This function requires `selenium` and `webdriver-manager` to be installed.
    It performs a best-effort login by looking for input fields named
    'username'/'user' and 'password', and a submit button.
    """
    if webdriver is None:
        raise RuntimeError("selenium is not available")

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    try:
        driver.get(login_url)
        sleep(1)
        # try to fill in username and password fields
        input_user = None
        input_pass = None
        for name in ("username", "user", "email", "login"):
            try:
                input_user = driver.find_element(By.NAME, name)
                break
            except Exception:
                input_user = None
        for name in ("password", "pass", "pwd"):
            try:
                input_pass = driver.find_element(By.NAME, name)
                break
            except Exception:
                input_pass = None

        if input_user is not None and input_pass is not None:
            input_user.clear()
            input_user.send_keys(username)
            input_pass.clear()
            input_pass.send_keys(password)
            # try submit
            try:
                input_pass.submit()
            except Exception:
                try:
                    driver.find_element(By.XPATH, "//button[@type='submit']").click()
                except Exception:
                    pass
            sleep(3)

        # collect cookies
        cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
        return cookies
    finally:
        driver.quit()


def validate_local_site(root: Path = HTML_DIR) -> list[str]:
    """Basic link checker: ensure internal ./pages/ links resolve to files.

    Returns a list of broken link descriptions.
    """
    broken: list[str] = []
    for html_path in root.rglob("*.html"):
        text = html_path.read_text(encoding="utf8")
        soup = BeautifulSoup(text, "html.parser")
        for a in soup.find_all("a"):
            href = a.get("href")
            if not href or href.startswith("http"):
                continue
            candidate = (html_path.parent / href).resolve()
            # normalize removing './'
            if not candidate.exists():
                broken.append(f"{html_path}: broken link {href}")
    return broken
