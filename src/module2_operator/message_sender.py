"""Message sender for chat interfaces."""

import time

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from src.models.platform_config import PlatformConfig
from src.selenium_utils.wait_helpers import wait_for_clickable, wait_for_element
from src.utils.exceptions import SelectorNotFoundException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MessageSender:
    """Sends messages through web chat interface."""

    def __init__(self, driver: WebDriver, config: PlatformConfig):
        """
        Initialize message sender.

        Args:
            driver: WebDriver instance
            config: Platform configuration
        """
        self.driver = driver
        self.config = config

    def send_message(self, text: str, retries: int = 3) -> None:
        """
        Send a message through the chat interface.

        Args:
            text: Message text to send
            retries: Number of retry attempts

        Raises:
            SelectorNotFoundException: If sending fails after retries
        """
        logger.info(f"Sending message: {text[:100]}...")

        for attempt in range(retries):
            try:
                # Find and focus input field
                input_field = wait_for_element(
                    self.driver,
                    self.config.selectors.input_field,
                    timeout=self.config.wait_timeouts.element_visible,
                )

                # Clear existing text (some platforms need this)
                try:
                    input_field.clear()
                except Exception:
                    # Some contenteditable divs don't support clear()
                    # Try selecting all and deleting
                    try:
                        input_field.send_keys(Keys.CONTROL, "a")
                        input_field.send_keys(Keys.DELETE)
                    except Exception as e:
                        logger.warning(f"Could not clear input field: {e}")

                # Type message
                input_field.send_keys(text)

                # Small delay for UI to update
                time.sleep(0.5)

                # Click send button
                send_button = wait_for_clickable(
                    self.driver,
                    self.config.selectors.send_button,
                    timeout=self.config.wait_timeouts.element_visible,
                )
                send_button.click()

                # Wait for message to be sent
                time.sleep(self.config.wait_timeouts.message_send)

                logger.info("✅ Message sent successfully")
                return

            except (
                StaleElementReferenceException,
                TimeoutException,
                NoSuchElementException,
            ) as e:
                if attempt < retries - 1:
                    logger.warning(
                        f"Send failed (attempt {attempt + 1}/{retries}), retrying..."
                    )
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"Failed to send message after {retries} attempts")
                    raise SelectorNotFoundException(
                        f"Could not send message after {retries} attempts. "
                        f"Selectors may be outdated. Consider recalibration."
                    ) from e

    def send_message_with_enter(self, text: str, retries: int = 3) -> None:
        """
        Send message using Enter key instead of button click.

        Some platforms support sending with Enter key.

        Args:
            text: Message text to send
            retries: Number of retry attempts
        """
        logger.info(f"Sending message (Enter key): {text[:100]}...")

        for attempt in range(retries):
            try:
                # Find input field
                input_field = wait_for_element(
                    self.driver,
                    self.config.selectors.input_field,
                    timeout=self.config.wait_timeouts.element_visible,
                )

                # Clear and type
                input_field.clear()
                input_field.send_keys(text)

                # Send with Enter
                input_field.send_keys(Keys.RETURN)

                # Wait for send
                time.sleep(self.config.wait_timeouts.message_send)

                logger.info("✅ Message sent (Enter)")
                return

            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(f"Send failed (attempt {attempt + 1}), retrying...")
                    time.sleep(1)
                    continue
                else:
                    logger.error(f"Failed to send message after {retries} attempts")
                    raise SelectorNotFoundException(
                        f"Could not send message: {e}"
                    ) from e
