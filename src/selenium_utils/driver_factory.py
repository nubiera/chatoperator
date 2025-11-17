"""WebDriver factory for creating and configuring browser instances."""

from typing import Literal, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from src.utils.logger import setup_logger
from src.utils.session_manager import SessionManager

logger = setup_logger(__name__)

# Global session manager instance
_session_manager = SessionManager()


def create_driver(
    headless: bool = True,
    browser: Literal["chrome", "firefox"] = "chrome",
    platform_name: Optional[str] = None,
    url: Optional[str] = None,
    load_session: bool = True,
) -> webdriver.Remote:
    """
    Create a WebDriver instance with consistent configuration.

    Args:
        headless: Whether to run in headless mode
        browser: Browser type ("chrome" or "firefox")
        platform_name: Optional platform name for session persistence
        url: Optional URL to navigate to (required if loading session)
        load_session: Whether to load saved session cookies (default: True)

    Returns:
        Configured WebDriver instance

    Notes:
        - If platform_name and url are provided, will attempt to load saved session
        - Navigate to url first, then load cookies (cookies are domain-specific)
        - Use save_driver_session() before quitting to persist the session
    """
    logger.info(f"Creating {browser} driver (headless={headless})")

    if browser == "chrome":
        driver = _create_chrome_driver(headless)
    elif browser == "firefox":
        driver = _create_firefox_driver(headless)
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    # Load saved session if requested
    if load_session and platform_name and url:
        if _session_manager.has_session(platform_name):
            logger.info(f"Found saved session for {platform_name}, loading...")

            # Navigate to URL first (cookies are domain-specific)
            logger.debug(f"Navigating to {url} to set domain for cookies...")
            driver.get(url)

            # Small wait for page to load
            import time
            time.sleep(2)

            # Load cookies
            if _session_manager.load_session(driver, platform_name):
                # Refresh page to apply cookies
                logger.debug("Refreshing page to apply session cookies...")
                driver.refresh()
                time.sleep(2)
                logger.info("✓ Session loaded successfully")
            else:
                logger.warning("Failed to load session, manual login may be required")
        else:
            logger.info(f"No saved session for {platform_name}, manual login required")

    return driver


def save_driver_session(driver: webdriver.Remote, platform_name: str) -> bool:
    """
    Save current browser session for a platform.

    Args:
        driver: WebDriver instance with active session
        platform_name: Platform name to save session for

    Returns:
        True if saved successfully, False otherwise

    Usage:
        driver = create_driver(platform_name="Tinder", url="https://tinder.com")
        # ... do work ...
        save_driver_session(driver, "Tinder")  # Save before quitting
        driver.quit()
    """
    return _session_manager.save_session(driver, platform_name)


def delete_driver_session(platform_name: str) -> bool:
    """
    Delete saved session for a platform (force fresh login next time).

    Args:
        platform_name: Platform name to delete session for

    Returns:
        True if deleted successfully, False otherwise
    """
    return _session_manager.delete_session(platform_name)


def has_saved_session(platform_name: str) -> bool:
    """
    Check if a saved session exists for a platform.

    Args:
        platform_name: Platform name to check

    Returns:
        True if session exists, False otherwise
    """
    return _session_manager.has_session(platform_name)


def _create_chrome_driver(headless: bool) -> webdriver.Chrome:
    """Create Chrome WebDriver with optimized settings."""
    options = ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    # Common Chrome arguments for stability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")

    # User agent to avoid detection
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Disable automation flags
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Use webdriver-manager for automatic driver management
    service = ChromeService(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)

    # Additional anti-detection measures
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        },
    )

    return driver


def _create_firefox_driver(headless: bool) -> webdriver.Firefox:
    """Create Firefox WebDriver with optimized settings."""
    options = FirefoxOptions()

    if headless:
        options.add_argument("--headless")

    # Common Firefox arguments
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    # User agent
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) "
        "Gecko/20100101 Firefox/120.0",
    )

    # Use webdriver-manager for automatic driver management
    service = FirefoxService(GeckoDriverManager().install())

    driver = webdriver.Firefox(service=service, options=options)

    return driver
