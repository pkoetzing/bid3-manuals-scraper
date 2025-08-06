#!/usr/bin/env python3
"""
Main script to run the Bid3 Manuals Scraper.

This script handles the installation of dependencies and execution
of the scraper with proper error handling and logging.
"""

import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def install_dependencies():
    """Install required dependencies using uv."""
    logger.info('Installing dependencies...')
    try:
        # Install main dependencies
        subprocess.run([
            'uv', 'pip', 'install',
            'selenium>=4.0.0',
            'beautifulsoup4>=4.0.0',
            'python-dotenv>=1.0.0',
            'webdriver-manager>=4.0.0'
        ], check=True)

        # Install dev dependencies
        subprocess.run([
            'uv', 'pip', 'install',
            'ruff>=0.6.0',
            'mypy>=1.0.0'
        ], check=True)

        logger.info('Dependencies installed successfully')
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f'Failed to install dependencies: {e}')
        return False
    except FileNotFoundError:
        logger.error('uv not found. Please install uv first.')
        logger.info(
            'Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh'
        )
        return False


def check_environment():
    """Check if environment is properly set up."""
    logger.info('Checking environment...')

    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning('.env file not found')
        logger.info(
            'Please copy .env.template to .env and fill in your credentials'
        )
        return False

    # Check if output directory exists
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    logger.info('Environment check passed')
    return True


def run_scraper():
    """Run the Bid3 manuals scraper using uv run."""
    logger.info('Starting Bid3 Manuals Scraper...')

    try:
        # Use uv run to execute the scraper in the correct environment
        result = subprocess.run([
            'uv', 'run', 'python', 'scraper.py'
        ], check=True, capture_output=True, text=True)

        logger.info('Scraper output:')
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(f'Scraper warnings: {result.stderr}')

        logger.info('Scraping completed successfully')
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f'Scraping failed with exit code {e.returncode}')
        if e.stdout:
            logger.error(f'Stdout: {e.stdout}')
        if e.stderr:
            logger.error(f'Stderr: {e.stderr}')
        return False
    except FileNotFoundError:
        logger.error('uv not found. Please install uv first.')
        return False
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        return False


def main():
    """Main entry point."""
    logger.info('Bid3 Manuals Scraper - Starting')

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Run scraper
    if not run_scraper():
        sys.exit(1)

    logger.info('All operations completed successfully')


if __name__ == '__main__':
    main()
