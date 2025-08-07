"""
Bid3 Manuals Scraper (fixed version)

This module provides functionality to scrape and download manual pages
from the Bid3 portal as .mhtml files for offline use.  Compared to the
original `scraper.py`, this version writes MHTML files in binary mode
and waits for pages to finish loading before capturing the snapshot. Without
these changes, the output MHTML can be incomplete or corrupted (e.g.,
missing embedded CSS and images), which may render as a blank page when
viewed offline.
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('scraper.log')
    ]
)

logger = logging.getLogger(__name__)


class Bid3ManualsScraper:
    """Scraper for Bid3 manual pages."""

    def __init__(
            self,
            output_dir: str = 'output',
            urls_path: str = 'manual_urls.json'):
        """
        Initialize the scraper.

        Args:
            output_dir: Directory to save downloaded files
            urls_path: Path to JSON file with manual URLs
        """
        load_dotenv()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Create subfolders for user_manual and technical_manual
        self.user_manual_dir = self.output_dir / 'user_manual'
        self.technical_manual_dir = self.output_dir / 'technical_manual'
        self.user_manual_dir.mkdir(exist_ok=True)
        self.technical_manual_dir.mkdir(exist_ok=True)

        self.username = os.getenv('BID3_USERNAME')
        self.password = os.getenv('BID3_PASSWORD')

        if not self.username or not self.password:
            raise ValueError(
                'BID3_USERNAME and BID3_PASSWORD must be set in .env file')

        self.base_url = 'https://bid3.afry.com'
        self.downloaded_urls: set[str] = set()
        self.driver: webdriver.Chrome | None = None

        # Load manual URLs from JSON file
        with open(urls_path, encoding='utf-8') as f:
            self.manual_urls = json.load(f)

    def _setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        # Uncomment and set if you have a custom Chrome install:
        # chrome_options.binary_location = (
        #     "C:/Program Files/Google/Chrome/Application/chrome.exe")

        # Use webdriver-manager to automatically download correct ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def _login(self) -> bool:
        """
        Login to the Bid3 portal.

        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            return False

        try:
            logger.info('Attempting to login to Bid3 portal')
            self.driver.get(self.base_url)
            logger.info(f'Navigated to {self.base_url}')

            # Navigate to the login page
            login_url = f'{self.base_url}/other/cloudlogin.html'
            self.driver.get(login_url)
            logger.info(f'Navigated to login page: {login_url}')

            # Wait for page to load
            time.sleep(3)
            logger.info(f'Current URL: {self.driver.current_url}')
            logger.info(f'Page title: {self.driver.title}')

            # Wait for login form to load
            wait = WebDriverWait(self.driver, 10)

            # Find username field by name (it uses name="name")
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, 'name'))
            )
            logger.info('Found username field with name: name')

            if self.username:
                username_field.send_keys(self.username)
                logger.info('Username entered')

            # Find password field by name (it uses name="pwd")
            password_field = self.driver.find_element(By.NAME, 'pwd')
            logger.info('Found password field with name: pwd')

            if self.password:
                password_field.send_keys(self.password)
                logger.info('Password entered')

            # Submit login form
            # (look for submit button with name="portletlogin")
            login_button = self.driver.find_element(
                By.NAME, 'portletlogin'
            )
            logger.info('Found login button (portletlogin)')

            login_button.click()
            logger.info('Login button clicked')

            # Wait for login to complete
            time.sleep(5)

            # Check if login was successful
            current_url = self.driver.current_url
            logger.info(f'Post-login URL: {current_url}')
            logger.info(f'Post-login title: {self.driver.title}')

            if ('login' not in current_url.lower()
                    and 'error' not in current_url.lower()):
                logger.info('Login successful')
                return True
            else:
                logger.error(
                    'Login failed - still on login page or error page')
                return False

        except Exception as e:
            logger.error(f'Login error: {e}')
            return False

    def _generate_filename_and_folder(self, url: str) -> tuple[Path, str]:
        """
        Generate output folder and filename based on URL.

        Args:
            url: The URL to generate filename and folder for

        Returns:
            (output_folder, filename)
        """
        # Remove base URL prefix
        path = url.replace(f'{self.base_url}/pages/', '')
        parts = path.split('/')
        if len(parts) >= 2:
            manual_type = parts[0]  # user-manual or technical-manual
            page_title = parts[1].replace('.html', '')
            if len(parts) > 2:
                subpage = '/'.join(parts[2:]).replace('.html', '')
                page_title = f'{page_title}_{subpage}'
            filename = f'{page_title}.mhtml'
            if manual_type == 'user-manual':
                folder = self.user_manual_dir
            elif manual_type == 'technical-manual':
                folder = self.technical_manual_dir
            else:
                folder = self.output_dir
        else:
            filename = path.replace('/', '_').replace('.html', '.mhtml')
            folder = self.output_dir
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return folder, filename

    def _save_page_as_mhtml(self, url: str) -> bool:
        """
        Save the currently loaded page as an MHTML file.

        Chrome's DevTools API returns the MHTML document as a UTF-8 string,
        but it may contain binary sections.  Writing with a text file handle
        or the wrong encoding can corrupt the archive and result in blank
        pages when viewed later.  To avoid this, we always encode the
        returned string to bytes and write it with a binary file handle.

        Args:
            url: URL of the page to save

        Returns:
            True if the file was saved successfully, False otherwise.
        """
        if not self.driver:
            return False

        try:
            folder, filename = self._generate_filename_and_folder(url)
            folder.mkdir(exist_ok=True)
            filepath = folder / filename

            # Ensure the DOM is fully loaded before capturing.  Without this
            # step the DevTools snapshot may miss late-loading assets or
            # incomplete markup which can lead to a blank page on replay.
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script(
                    'return document.readyState') == 'complete')
            # Small additional wait to allow asynchronous resources to finish
            time.sleep(2)

            # Capture the page as MHTML via the Chrome DevTools Protocol
            result = self.driver.execute_cdp_cmd(
                'Page.captureSnapshot',
                {'format': 'mhtml'}
            )

            mhtml_content: str = result.get('data', '')
            if not mhtml_content:
                logger.error(f'No MHTML data returned for {url}')
                return False

            # Persist MHTML content to disk using binary mode.  The string
            # returned by captureSnapshot is UTF-8 encoded; encoding it
            # explicitly and writing bytes preserves CRLF line endings and
            # embedded binary data.
            with open(filepath, 'wb') as f:
                f.write(mhtml_content.encode('utf-8'))

            logger.info(f'Saved: {filename}')
            return True

        except Exception as e:
            logger.error(f'Error saving {url}: {e}')
            return False

    def _get_subpage_links(self, url: str) -> list[str]:
        """
        Extract subpage links from the current page.

        Args:
            url: Current page URL to extract links from

        Returns:
            List of subpage URLs with the same prefix
        """
        if not self.driver:
            return []

        try:
            # Parse page content
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            links: list[str] = []

            # Find all links
            for link in soup.find_all('a', href=True):
                if not isinstance(link, Tag):
                    continue

                href = link.get('href')
                if not href:
                    continue

                # Convert relative URLs to absolute
                absolute_url = urljoin(url, str(href))

                # Check if link starts with same prefix as parent page
                parent_prefix = url.rsplit('/', 1)[0] + '/'
                if absolute_url.startswith(parent_prefix):
                    # Ensure it's an HTML page
                    if absolute_url.endswith('.html'):
                        links.append(absolute_url)

            # Remove duplicates by converting to a set
            return list(set(links))

        except Exception as e:
            logger.error(f'Error extracting links from {url}: {e}')
            return []

    def download_page_recursive(self, url: str) -> None:
        """
        Download the specified page and recursively download its subpages.

        Args:
            url: URL to download
        """
        if not self.driver:
            return

        # Skip if already downloaded
        if url in self.downloaded_urls:
            logger.info(f'Already downloaded: {url}')
            return

        try:
            logger.info(f'Downloading: {url}')

            # Navigate to page
            self.driver.get(url)
            time.sleep(2)  # Wait for initial page load

            # Save page as MHTML
            if self._save_page_as_mhtml(url):
                self.downloaded_urls.add(url)

            # Get subpage links
            subpage_links = self._get_subpage_links(url)

            # Recursively download subpages
            for subpage_url in subpage_links:
                if subpage_url not in self.downloaded_urls:
                    self.download_page_recursive(subpage_url)

        except Exception as e:
            logger.error(f'Error downloading {url}: {e}')

    def scrape_manuals(self) -> None:
        """Main method to scrape all manual pages."""
        try:
            # Setup driver
            self.driver = self._setup_driver()

            # Login
            if not self._login():
                logger.error('Failed to login. Exiting.')
                return

            # Download User Manual pages
            logger.info('Starting User Manual downloads')
            for url in self.manual_urls.get('user_manual', []):
                self.download_page_recursive(url)

            # Download Technical Manual pages
            logger.info('Starting Technical Manual downloads')
            for url in self.manual_urls.get('technical_manual', []):
                self.download_page_recursive(url)

            downloaded_count = len(self.downloaded_urls)
            logger.info(
                f'Scraping complete. Downloaded {downloaded_count} pages.'
            )

        except Exception as e:
            logger.error(f'Scraping error: {e}')
        finally:
            if self.driver:
                self.driver.quit()


def main() -> None:
    """Main entry point."""
    scraper = Bid3ManualsScraper()
    scraper.scrape_manuals()


if __name__ == '__main__':
    main()
