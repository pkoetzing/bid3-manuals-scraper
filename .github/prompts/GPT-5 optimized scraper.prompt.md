# Role and Objective
- Develop a web scraper to mirror a set of web pages for offline use, based on URLs provided in `manuals_url.json`.

# Workflow Checklist
Begin with a concise checklist (3-7 bullets) of what you will do; keep items conceptual, not implementation-level:
1. Load starting URLs from `manuals_url.json`.
2. Identify target pages and resources within allowed path scope.
3. Download HTML content and all related assets (CSS, JS, images).
4. Update internal links and resource references for offline navigation.
5. Save content to the `html` directory, preserving site structure.
6. Validate that navigation and resources function offline; fix issues if found.

# Instructions
- Read all starting URLs from `manuals_url.json`.
- For each URL, download the page itself and all pages linked within the same path (i.e., subpages and sibling pages within the directory).
- Ensure all related resources (HTML, CSS, JavaScript, images) required for full local functionality are downloaded.
- Update internal links and resource references so navigation and media work correctly offline.

# Scope
- Only handle URLs that start with `https://bid3.afry.com/pages/`.
- For a starting URL like `https://bid3.afry.com/pages/technical-manual/bid3-db-structure.html`, include all linked pages under `https://bid3.afry.com/pages/technical-manual/bid3-db-structure/`.

# Local Directory Structure
- Store the downloaded pages in an `html` subfolder, mirroring the online site's relative folder/file layout.
    - Example: `https://bid3.afry.com/pages/technical-manual/bid3-db-structure.html` becomes `html/technical-manual/bid3-db-structure.html`

# Output Format
- Save files in the `html` directory with a structure that matches the online site.

# Validation
After each page download and rewrite of internal references, validate that local navigation and resources work by checking links and references. If issues are detected, self-correct and retry the affected step.

# Stop Conditions
- All linked content and resources within each starting URL's directory are downloaded.
- All internal references are updated; the offline site is fully navigable.