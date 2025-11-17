"""Reusable explicit wait patterns for Selenium."""


from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def wait_for_element(
    driver: WebDriver,
    selector: str,
    by: By = By.CSS_SELECTOR,
    timeout: int = settings.ELEMENT_VISIBLE_TIMEOUT,
) -> WebElement:
    """
    Wait for element to be present in the DOM.

    Args:
        driver: WebDriver instance
        selector: Element selector
        by: Locator strategy (default: CSS_SELECTOR)
        timeout: Maximum wait time in seconds

    Returns:
        WebElement when found

    Raises:
        TimeoutException: If element not found within timeout
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        logger.debug(f"Element found: {selector}")
        return element
    except TimeoutException:
        logger.error(f"Element not found after {timeout}s: {selector}")
        raise


def wait_for_clickable(
    driver: WebDriver,
    selector: str,
    by: By = By.CSS_SELECTOR,
    timeout: int = settings.ELEMENT_VISIBLE_TIMEOUT,
) -> WebElement:
    """
    Wait for element to be clickable.

    Args:
        driver: WebDriver instance
        selector: Element selector
        by: Locator strategy (default: CSS_SELECTOR)
        timeout: Maximum wait time in seconds

    Returns:
        Clickable WebElement

    Raises:
        TimeoutException: If element not clickable within timeout
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        logger.debug(f"Element clickable: {selector}")
        return element
    except TimeoutException:
        logger.error(f"Element not clickable after {timeout}s: {selector}")
        raise


def wait_for_text_in_element(
    driver: WebDriver,
    selector: str,
    text: str,
    by: By = By.CSS_SELECTOR,
    timeout: int = settings.ELEMENT_VISIBLE_TIMEOUT,
) -> bool:
    """
    Wait for specific text to appear in an element.

    Args:
        driver: WebDriver instance
        selector: Element selector
        text: Expected text
        by: Locator strategy (default: CSS_SELECTOR)
        timeout: Maximum wait time in seconds

    Returns:
        True if text found

    Raises:
        TimeoutException: If text not found within timeout
    """
    try:
        result = WebDriverWait(driver, timeout).until(
            EC.text_to_be_present_in_element((by, selector), text)
        )
        logger.debug(f"Text '{text}' found in element: {selector}")
        return result
    except TimeoutException:
        logger.error(f"Text '{text}' not found in element {selector} after {timeout}s")
        raise


def wait_for_page_load(
    driver: WebDriver, timeout: int = settings.PAGE_LOAD_TIMEOUT
) -> bool:
    """
    Wait for page to finish loading (document.readyState == 'complete').

    Args:
        driver: WebDriver instance
        timeout: Maximum wait time in seconds

    Returns:
        True if page loaded

    Raises:
        TimeoutException: If page doesn't load within timeout
    """
    try:

        def page_ready(driver: WebDriver) -> bool:
            return driver.execute_script("return document.readyState") == "complete"

        WebDriverWait(driver, timeout).until(page_ready)
        logger.debug("Page load complete")
        return True
    except TimeoutException:
        logger.error(f"Page did not load after {timeout}s")
        raise


def wait_for_element_to_disappear(
    driver: WebDriver,
    selector: str,
    by: By = By.CSS_SELECTOR,
    timeout: int = settings.ELEMENT_VISIBLE_TIMEOUT,
) -> bool:
    """
    Wait for element to disappear from the DOM.

    Args:
        driver: WebDriver instance
        selector: Element selector
        by: Locator strategy (default: CSS_SELECTOR)
        timeout: Maximum wait time in seconds

    Returns:
        True if element disappeared

    Raises:
        TimeoutException: If element still present after timeout
    """
    try:
        result = WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((by, selector))
        )
        logger.debug(f"Element disappeared: {selector}")
        return result
    except TimeoutException:
        logger.error(f"Element still present after {timeout}s: {selector}")
        raise
