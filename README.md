# Bid3 Manuals Scraper

A Python tool to scrape and download Bid3 manual pages from the AFRY portal for offline use.

## Features

- Downloads User Manual and Technical Manual pages as .mhtml files
- Recursively follows links to download subpages
- Avoids duplicate downloads
- Generates organized filenames based on manual type and page title
- Uses headless Chrome automation for reliable page rendering

## Requirements

- Python 3.12+
- uv (Python package manager)
- ChromeDriver
- Bid3 portal credentials

## Setup

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Download ChromeDriver**:
   - Download from [ChromeDriver Downloads](https://chromedriver.chromium.org/)
   - Place `chromedriver.exe` in the project root directory

3. **Configure credentials**:
   ```bash
   cp .env.template .env
   ```
   Edit `.env` and add your Bid3 portal credentials:
   ```
   BID3_USERNAME=your_username
   BID3_PASSWORD=your_password
   ```

## Usage

Run the scraper:

```bash
python main.py
```

The script will:
1. Install required dependencies
2. Check environment setup
3. Login to the Bid3 portal
4. Download all manual pages and subpages
5. Save files in the `output/` directory

## Output

Downloaded files are saved in the `output/` directory with the naming convention:
- `user-manual_page-title.mhtml`
- `technical-manual_page-title.mhtml`

For subpages, the filename includes the full path:
- `user-manual_inputs_standing-data.mhtml`

## Manual Pages Downloaded

### User Manual (8 pages)
- Installing Bid3
- Getting Started
- Inputs
- Running Bid3
- Outputs
- Additional Features
- Bid3 Short Term
- Common Warnings and Errors

### Technical Manual (14 pages)
- Auto Build Module
- Policy Build Module
- Banding Module
- Calendar Constraints
- Dispatch Module
- Economics Modules
- Fuel Mode Module
- Redispatch Module
- Retail Module
- SOS Module
- LOLE Module
- Water Value Modules
- Co-products
- Nodal Modelling
- Bid3 DB Structure

## Development

The project uses:
- **ruff** for code formatting and linting
- **mypy** for type checking
- **selenium** for browser automation
- **beautifulsoup4** for HTML parsing
- **python-dotenv** for environment variable management

## Logging

The scraper logs activity to both console and `scraper.log` file.
Log levels include INFO for general progress and ERROR for issues.

## Error Handling

The scraper includes retry logic and graceful error handling for:
- Network timeouts
- Authentication failures
- Missing pages
- File system errors
