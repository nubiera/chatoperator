"""Safe element interaction helpers with retry logic."""

import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from src.selenium_utils.wait_helpers import wait_for_clickable, wait_for_element
from src.utils.exceptions import SelectorNotFoundException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def safe_click(
    driver: WebDriver,
    selector: str,
    by: By = By.CSS_SELECTOR,
    retries: int = 3,
    retry_delay: float = 0.5,
) -> None:
    """
    Click element with retry logic for stale elements.

    Args:
        driver: WebDriver instance
        selector: Element selector
        by: Locator strategy (default: CSS_SELECTOR)
        retries: Number of retry attempts
        retry_delay: Delay between retries in seconds

    Raises:
        SelectorNotFoundException: If element cannot be clicked after retries
    """
    for attempt in range(retries):
        try:
            element = wait_for_clickable(driver, selector, by=by)
            element.click()
            logger.debug(f"Clicked element: {selector}")
            return
        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            if attempt < retries - 1:
                logger.warning(
                    f"Click failed (attempt {attempt + 1}/{retries}): {selector}. Retrying..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Failed to click element after {retries} attempts: {selector}")
                raise SelectorNotFoundException(
                    f"Could not click element after {retries} attempts: {selector}"
                ) from e


def safe_send_keys(
    driver: WebDriver,
    selector: str,
    text: str,
    by: By = By.CSS_SELECTOR,
    clear_first: bool = True,
    retries: int = 3,
    retry_delay: float = 0.5,
) -> None:
    """
    Send keys to element with retry logic.

    Args:
        driver: WebDriver instance
        selector: Element selector
        text: Text to send
        by: Locator strategy (default: CSS_SELECTOR)
        clear_first: Whether to clear element before sending keys
        retries: Number of retry attempts
        retry_delay: Delay between retries in seconds

    Raises:
        SelectorNotFoundException: If keys cannot be sent after retries
    """
    for attempt in range(retries):
        try:
            element = wait_for_element(driver, selector, by=by)

            if clear_first:
                element.clear()

            element.send_keys(text)
            logger.debug(f"Sent keys to element: {selector}")
            return
        except StaleElementReferenceException as e:
            if attempt < retries - 1:
                logger.warning(
                    f"Send keys failed (attempt {attempt + 1}/{retries}): {selector}. "
                    f"Retrying..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(
                    f"Failed to send keys to element after {retries} attempts: {selector}"
                )
                raise SelectorNotFoundException(
                    f"Could not send keys after {retries} attempts: {selector}"
                ) from e


def safe_get_text(
    driver: WebDriver,
    selector: str,
    by: By = By.CSS_SELECTOR,
    retries: int = 3,
    retry_delay: float = 0.5,
) -> str:
    """
    Get text from element with retry logic.

    Args:
        driver: WebDriver instance
        selector: Element selector
        by: Locator strategy (default: CSS_SELECTOR)
        retries: Number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Element text content

    Raises:
        SelectorNotFoundException: If text cannot be retrieved after retries
    """
    for attempt in range(retries):
        try:
            element = wait_for_element(driver, selector, by=by)
            text = element.text
            logger.debug(f"Got text from element: {selector}")
            return text
        except StaleElementReferenceException as e:
            if attempt < retries - 1:
                logger.warning(
                    f"Get text failed (attempt {attempt + 1}/{retries}): {selector}. Retrying..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(
                    f"Failed to get text from element after {retries} attempts: {selector}"
                )
                raise SelectorNotFoundException(
                    f"Could not get text after {retries} attempts: {selector}"
                ) from e


def safe_get_attribute(
    driver: WebDriver,
    selector: str,
    attribute: str,
    by: By = By.CSS_SELECTOR,
    retries: int = 3,
    retry_delay: float = 0.5,
) -> str | None:
    """
    Get attribute from element with retry logic.

    Args:
        driver: WebDriver instance
        selector: Element selector
        attribute: Attribute name
        by: Locator strategy (default: CSS_SELECTOR)
        retries: Number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Attribute value or None

    Raises:
        SelectorNotFoundException: If attribute cannot be retrieved after retries
    """
    for attempt in range(retries):
        try:
            element = wait_for_element(driver, selector, by=by)
            value = element.get_attribute(attribute)
            logger.debug(f"Got attribute '{attribute}' from element: {selector}")
            return value
        except StaleElementReferenceException as e:
            if attempt < retries - 1:
                logger.warning(
                    f"Get attribute failed (attempt {attempt + 1}/{retries}): "
                    f"{selector}. Retrying..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(
                    f"Failed to get attribute from element after {retries} attempts: {selector}"
                )
                raise SelectorNotFoundException(
                    f"Could not get attribute after {retries} attempts: {selector}"
                ) from e


def get_element_safely(
    driver: WebDriver,
    selector: str,
    by: By = By.CSS_SELECTOR,
    retries: int = 3,
    retry_delay: float = 0.5,
) -> WebElement:
    """
    Get element with retry logic for stale references.

    Args:
        driver: WebDriver instance
        selector: Element selector
        by: Locator strategy (default: CSS_SELECTOR)
        retries: Number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        WebElement instance

    Raises:
        SelectorNotFoundException: If element cannot be retrieved after retries
    """
    for attempt in range(retries):
        try:
            element = wait_for_element(driver, selector, by=by)
            # Test that element is still attached by accessing a property
            _ = element.tag_name
            logger.debug(f"Got element safely: {selector}")
            return element
        except StaleElementReferenceException as e:
            if attempt < retries - 1:
                logger.warning(
                    f"Get element failed (attempt {attempt + 1}/{retries}): "
                    f"{selector}. Retrying..."
                )
                time.sleep(retry_delay)
                continue
            else:
                logger.error(
                    f"Failed to get element after {retries} attempts: {selector}"
                )
                raise SelectorNotFoundException(
                    f"Could not get element after {retries} attempts: {selector}"
                ) from e
