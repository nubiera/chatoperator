"""Screenshot capture functionality."""

import time

from selenium.webdriver.remote.webdriver import WebDriver

from src.selenium_utils.wait_helpers import wait_for_page_load
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def capture_screenshot(driver: WebDriver, wait_seconds: int = 2) -> bytes:
    """
    Capture full-page screenshot.

    Args:
        driver: WebDriver instance
        wait_seconds: Additional wait time for dynamic content (default: 2)

    Returns:
        PNG screenshot as bytes
    """
    logger.info("Capturing screenshot...")

    # Wait for page to fully load
    wait_for_page_load(driver)

    # Maximize window for consistent screenshots
    driver.maximize_window()

    # Additional wait for dynamic content to load
    # This is one of the few acceptable uses of sleep in the codebase
    if wait_seconds > 0:
        logger.debug(f"Waiting {wait_seconds}s for dynamic content...")
        time.sleep(wait_seconds)

    # Capture screenshot as PNG bytes
    screenshot_bytes = driver.get_screenshot_as_png()

    logger.info(f"Screenshot captured ({len(screenshot_bytes)} bytes)")
    return screenshot_bytes
