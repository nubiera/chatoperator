"""Main analyzer orchestrator for Module 1."""

import time
from datetime import datetime
from pathlib import Path

from src.config.settings import settings
from src.models.platform_config import (
    PlatformConfig,
    SelectorsModel,
    ArchiveSelectorsModel,
    WaitTimeoutsModel,
)
from src.module1_analyzer.cache_writer import write_cache
from src.module1_analyzer.dom_extractor import extract_dom
from src.module1_analyzer.gemini_client import GeminiClient
from src.module1_analyzer.screenshot_capturer import capture_screenshot
from src.selenium_utils.driver_factory import create_driver, save_driver_session
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
        include_archive: bool = False,
    ) -> PlatformConfig:
        """
        Analyze a chat platform and generate configuration cache.

        Args:
            platform_name: Name of the platform
            url: URL of the platform
            wait_after_load: Seconds to wait after page load for JS (default: 5)
            headless: Run browser in headless mode (default: False for initial analysis)
            focus_selector: CSS selector to focus DOM extraction (default: "body")
            include_archive: Include archive selectors for conversation downloading (default: False)

        Returns:
            Generated PlatformConfig

        Raises:
            GeminiAPIException: If Gemini API fails
            SelectorNotFoundException: If critical selectors not found
        """
        logger.info(f"Starting analysis for platform: {platform_name}")
        logger.info(f"URL: {url}")

        # Create driver with session support
        driver = create_driver(
            headless=headless,
            browser=settings.DEFAULT_BROWSER,
            platform_name=platform_name,
            url=url,
        )

        try:

            # Wait for page to load and dynamic content
            logger.info(f"Waiting {wait_after_load}s for page content to load...")
            time.sleep(wait_after_load)

            # Capture screenshot
            screenshot_bytes = capture_screenshot(driver, wait_seconds=2)

            # Extract DOM
            html_content = extract_dom(driver, focus_selector=focus_selector)

            # Analyze with Gemini
            logger.info("Analyzing interface with Gemini Vision API...")
            analysis_result = self.gemini_client.analyze_interface(
                screenshot_bytes, html_content, platform_name, include_archive=include_archive
            )

            # Build configuration
            # Handle both old format (just selectors dict) and new format (with archive_selectors)
            if include_archive and isinstance(analysis_result, dict) and "archive_selectors" in analysis_result:
                # New format with archive_selectors
                config = PlatformConfig(
                    platform_name=platform_name,
                    url=url,
                    last_updated=datetime.now(),
                    selectors=SelectorsModel(**analysis_result["selectors"]),
                    archive_selectors=ArchiveSelectorsModel(**analysis_result["archive_selectors"]),
                    wait_timeouts=WaitTimeoutsModel(),  # Use defaults
                )
            else:
                # Old format or regular mode - just selectors
                config = PlatformConfig(
                    platform_name=platform_name,
                    url=url,
                    last_updated=datetime.now(),
                    selectors=SelectorsModel(**analysis_result),
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
            # Save session before cleanup
            save_driver_session(driver, platform_name)

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
