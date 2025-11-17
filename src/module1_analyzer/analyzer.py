"""Main analyzer orchestrator for Module 1."""

import time
from datetime import datetime
from pathlib import Path

from src.config.settings import settings
from src.models.platform_config import (
    PlatformConfig,
    SelectorsModel,
    WaitTimeoutsModel,
)
from src.module1_analyzer.cache_writer import write_cache
from src.module1_analyzer.dom_extractor import extract_dom
from src.module1_analyzer.gemini_client import GeminiClient
from src.module1_analyzer.screenshot_capturer import capture_screenshot
from src.selenium_utils.driver_factory import create_driver
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class InterfaceAnalyzer:
    """Analyzes chat interfaces using AI vision to generate configuration caches."""

    def __init__(self, gemini_api_key: str, cache_dir: Path):
        """
        Initialize the analyzer.

        Args:
            gemini_api_key: Google Gemini API key
            cache_dir: Directory to store configuration caches
        """
        self.gemini_client = GeminiClient(gemini_api_key)
        self.cache_dir = cache_dir
        logger.info("InterfaceAnalyzer initialized")

    def analyze_platform(
        self,
        platform_name: str,
        url: str,
        wait_after_load: int = 5,
        headless: bool = False,
        focus_selector: str = "body",
    ) -> PlatformConfig:
        """
        Analyze a chat platform and generate configuration cache.

        Args:
            platform_name: Name of the platform
            url: URL of the platform
            wait_after_load: Seconds to wait after page load for JS (default: 5)
            headless: Run browser in headless mode (default: False for initial analysis)
            focus_selector: CSS selector to focus DOM extraction (default: "body")

        Returns:
            Generated PlatformConfig

        Raises:
            GeminiAPIException: If Gemini API fails
            SelectorNotFoundException: If critical selectors not found
        """
        logger.info(f"Starting analysis for platform: {platform_name}")
        logger.info(f"URL: {url}")

        # Create driver
        driver = create_driver(headless=headless, browser=settings.DEFAULT_BROWSER)

        try:
            # Navigate to platform
            logger.info(f"Navigating to {url}...")
            driver.get(url)

            # Wait for page to load and dynamic content
            logger.info(f"Waiting {wait_after_load}s for page content to load...")
            time.sleep(wait_after_load)

            # Capture screenshot
            screenshot_bytes = capture_screenshot(driver, wait_seconds=2)

            # Extract DOM
            html_content = extract_dom(driver, focus_selector=focus_selector)

            # Analyze with Gemini
            logger.info("Analyzing interface with Gemini Vision API...")
            selectors_dict = self.gemini_client.analyze_interface(
                screenshot_bytes, html_content, platform_name
            )

            # Build configuration
            config = PlatformConfig(
                platform_name=platform_name,
                url=url,
                last_updated=datetime.now(),
                selectors=SelectorsModel(**selectors_dict),
                wait_timeouts=WaitTimeoutsModel(),  # Use defaults
            )

            # Write cache
            cache_file = write_cache(config, self.cache_dir)
            logger.info(f"✅ Analysis complete! Cache saved to: {cache_file}")

            return config

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

        finally:
            # Clean up
            logger.info("Closing browser...")
            driver.quit()

    def test_gemini_connection(self) -> bool:
        """
        Test Gemini API connection.

        Returns:
            True if connection successful
        """
        return self.gemini_client.test_connection()
