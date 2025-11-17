"""WebDriver factory for creating and configuring browser instances."""

from typing import Literal

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def create_driver(
    headless: bool = True, browser: Literal["chrome", "firefox"] = "chrome"
) -> webdriver.Remote:
    """
    Create a WebDriver instance with consistent configuration.

    Args:
        headless: Whether to run in headless mode
        browser: Browser type ("chrome" or "firefox")

    Returns:
        Configured WebDriver instance
    """
    logger.info(f"Creating {browser} driver (headless={headless})")

    if browser == "chrome":
        return _create_chrome_driver(headless)
    elif browser == "firefox":
        return _create_firefox_driver(headless)
    else:
        raise ValueError(f"Unsupported browser: {browser}")


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
