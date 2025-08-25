---
mode: 'agent'
model: 'GPT-5 mini (Preview)'
tools: ['codebase', 'editFiles', 'findTestFiles', 'problems', 'runCommands', 'runTasks', 'runTests', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', , 'installPythonPackage']
description: 'Download the Bid3 Manuals'
---

# Download Bid3 Manuals

## 1. Persistence
   You are an agent - please keep going until the user’s query
   is completely resolved, before ending your turn and yielding back to the user.
   Only terminate your turn when you are sure that the problem is solved.

## 2. Tool-calling
   If you are not sure about file content or codebase structure
   pertaining to the user’s request, use your tools to read files
   and gather the relevant information: do NOT guess or make up an answer.

## 3. Planning
   You MUST plan extensively before each function call, and reflect extensively
   on the outcomes of the previous function calls. DO NOT do this entire process
   by making function calls only, as this can impair your ability to solve
   the problem and think insightfully.

## 4. Tools and packages to use
- webdriver-manager
- selenium
- beautifulsoup4
- python-dotenv
- ruff
- mypy
- pytest

## 5. Project structure
- `cli.py`: Main command-line interface to run the scraper.
- `src/`: Core scraping logic, including functions for downloading pages and assets.
- `data/manuals_url.json`: JSON file containing the list of starting URLs to scrape.
- `html/`: Directory where the mirrored HTML files and assets will be stored.
- `tests/`: Unit tests for the scraper functions.
- `.env`: Environment file for storing sensitive information like login credentials.
- `.env.template`: Example environment file without sensitive data.
- `requirements.txt`: List of required Python packages.
- `README.md`: Documentation for the project.
- `pyproject.toml`: Project configuration file.

## 6. Login to the Bid3 Portal
url = https://bid3.afry.com/
Use webdriver-manager + selenium to log in with credentials from .env.
Extract cookies and populate requests.Session so crawl_directory can access authenticated content.
Use credentials from the .env file

## 7. Download the Bid3 Manual pages

### Role and Objective
- Develop a web scraper to mirror a set of web pages for offline use, based on URLs provided in `data\manuals_url.json`.

### Workflow Checklist
Begin with a concise checklist (3-7 bullets) of what you will do; keep items conceptual, not implementation-level:
1. Load starting URLs from `data\manuals_url.json`.
2. Identify target pages and resources within allowed path scope.
3. Download HTML content and all related assets (CSS, JS, images).
4. Update internal links and resource references for offline navigation.
5. Save content to the `html` directory, preserving site structure.
6. Validate that navigation and resources function offline; fix issues if found.

### Instructions
- Read all starting URLs from `data\manuals_url.json`.
- For each URL, download the page itself and all pages linked within the same path (i.e., subpages and sibling pages within the directory).
- Ensure all related resources (HTML, CSS, JavaScript, images) required for full local functionality are downloaded.
- Update internal links and resource references so navigation and media work correctly offline.

### Scope
- Only handle URLs that start with `https://bid3.afry.com/pages/`.
- For a starting URL like `https://bid3.afry.com/pages/technical-manual/bid3-db-structure.html`, include all linked pages under `https://bid3.afry.com/pages/technical-manual/bid3-db-structure/`.

### Local Directory Structure
- Store the downloaded pages in an `html` subfolder, mirroring the online site's relative folder/file layout.
    - Example: `https://bid3.afry.com/pages/technical-manual/bid3-db-structure.html` becomes `html/technical-manual/bid3-db-structure.html`

### Output Format
- Save files in the `html` directory with a structure that matches the online site.

### Hardening:
Improve asset URL heuristics (font files, inline CSS url(...) rewriting).
Handle query strings / duplicate filenames.
Add retries, rate-limiting, and user-agent.

### Validation
After each page download and rewrite of internal references, validate that local navigation and resources work by checking links and references. If issues are detected, self-correct and retry the affected step.
Add an automated post-scrape checker that loads saved HTML files and ensures internal links resolve (basic link-check).

### Stop Conditions
- All linked content and resources within each starting URL's directory are downloaded.
- All internal references are updated; the offline site is fully navigable.
