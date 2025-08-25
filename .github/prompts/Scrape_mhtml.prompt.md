---
mode: 'agent'
model: 'Claude Sonnet 3.5'
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
- uv: for creating and managing Python virtual environments
- chromedriver.exe: for controlling headless Chrome browsers
Update the pyproject.toml file to include the following packages:
- selenium
- beautifulsoup4
- python-dotenv
- ruff
- mypy

## 5. Login to the Bid3 Portal
url = https://bid3.afry.com/
use credentials from the .env file

## 5. Download the Bid3 Manual pages

Visit the following links for the Bid3 User manual and technical manual.
Download the pages as .mhtml files for offline use.
Recursively follow any links on the listed pages to access subpages.
Download all subpages as .mhtml files as well.
Use the links as filenames, starting with either user-manual or technical-manual,
followed by and underscore and the page title and .mhtml as the file extension.
Omit the common prefix https://bid3.afry.com/pages/.
E.g. https://bid3.afry.com/pages/user-manual/inputs.html downloaded
becomes user-manual_inputs.mhtml.
Only download pages that start with the same url as the parent page,
e.g. if the parent page is https://bid3.afry.com/pages/user-manual/inputs.html,
then only download pages that start with https://bid3.afry.com/pages/user-manual/inputs/
like https://bid3.afry.com/pages/user-manual/inputs/standing-data.html
Ignore any links that do not start with the same url prefix as the parent page.
Download any page only once, even if it is linked from multiple pages.
Save the downloaded files in the output folder

### User Manual
https://bid3.afry.com/pages/user-manual/installing-bid3.html
https://bid3.afry.com/pages/user-manual/getting-started.html
https://bid3.afry.com/pages/user-manual/inputs.html
https://bid3.afry.com/pages/user-manual/running-bid3.html
https://bid3.afry.com/pages/user-manual/outputs.html
https://bid3.afry.com/pages/user-manual/additional-features.html
https://bid3.afry.com/pages/user-manual/bid3-short-term.html
https://bid3.afry.com/pages/user-manual/common-warnings-and-errors.html

### Technical Manual
https://bid3.afry.com/pages/technical-manual/auto-build-module.html
https://bid3.afry.com/pages/technical-manual/policy-build-module.html
https://bid3.afry.com/pages/technical-manual/banding-module.html
https://bid3.afry.com/pages/technical-manual/calendar-constraints.html
https://bid3.afry.com/pages/technical-manual/dispatch-module.html
https://bid3.afry.com/pages/technical-manual/economics-modules.html
https://bid3.afry.com/pages/technical-manual/fuel-mode-module.html
https://bid3.afry.com/pages/technical-manual/redispatch-module.html
https://bid3.afry.com/pages/technical-manual/retail-module.html
https://bid3.afry.com/pages/technical-manual/sos-module.html
https://bid3.afry.com/pages/technical-manual/lole-module.html
https://bid3.afry.com/pages/technical-manual/water-value-modules.html
https://bid3.afry.com/pages/technical-manual/co-products.html
https://bid3.afry.com/pages/technical-manual/nodal-modelling.html
https://bid3.afry.com/pages/technical-manual/bid3-db-structure.html