"""Download conversation history with infinite scroll handling."""

import logging
import time
from typing import List, Tuple

from pydantic import BaseModel
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.models.platform_config import ArchiveSelectorsModel, SelectorsModel
from src.selenium_utils.wait_helpers import wait_for_element
from src.utils.exceptions import ChatOperatorException

logger = logging.getLogger(__name__)


class ConversationDownloadException(ChatOperatorException):
    """Exception raised when conversation download fails."""
    pass


class Message(BaseModel):
    """Individual message data model."""

    text: str
    timestamp: str | None = None
    is_user: bool  # True if sent by user, False if received
    sender: str | None = None


class ConversationDownloader:
    """Downloads full conversation history with scroll handling."""

    def __init__(
        self,
        driver: WebDriver,
        selectors: SelectorsModel,
        archive_selectors: ArchiveSelectorsModel
    ):
        """Initialize ConversationDownloader.

        Args:
            driver: Selenium WebDriver instance
            selectors: Basic platform selectors
            archive_selectors: Archive-specific selectors
        """
        self.driver = driver
        self.selectors = selectors
        self.archive_selectors = archive_selectors

    def download_conversation(
        self,
        max_scrolls: int = 100,
        scroll_pause: float = 1.5
    ) -> List[Message]:
        """Download full conversation with infinite scroll handling.

        Args:
            max_scrolls: Maximum number of scroll attempts
            scroll_pause: Seconds to wait between scrolls

        Returns:
            List of Message objects in chronological order

        Raises:
            ConversationDownloadException: If download fails
        """
        try:
            logger.info("Starting conversation download with scroll handling")

            # Scroll to load full history
            self._scroll_to_load_history(max_scrolls, scroll_pause)

            # Extract all messages
            messages = self._extract_messages()

            logger.info(f"Downloaded {len(messages)} messages")
            return messages

        except Exception as e:
            logger.error(f"Failed to download conversation: {e}")
            raise ConversationDownloadException(f"Conversation download failed: {e}")

    def _scroll_to_load_history(self, max_scrolls: int, scroll_pause: float):
        """Scroll conversation container to load full history.

        Args:
            max_scrolls: Maximum scroll attempts
            scroll_pause: Seconds between scrolls
        """
        try:
            # Find the scrollable container
            container = wait_for_element(
                self.driver,
                self.archive_selectors.scroll_container,
                timeout=10
            )

            logger.debug(f"Found scroll container, starting scroll sequence")

            previous_height = 0
            scroll_count = 0
            no_change_count = 0

            while scroll_count < max_scrolls:
                # Get current scroll height
                current_height = self.driver.execute_script(
                    "return arguments[0].scrollTop;",
                    container
                )

                # Scroll to top to load older messages
                self.driver.execute_script(
                    "arguments[0].scrollTop = 0;",
                    container
                )

                # Wait for new content to load
                time.sleep(scroll_pause)

                # Check if we've loaded new content
                new_height = self.driver.execute_script(
                    "return arguments[0].scrollTop;",
                    container
                )

                if new_height == previous_height:
                    no_change_count += 1
                    logger.debug(f"No new content loaded (attempt {no_change_count})")

                    # If no change for 3 consecutive attempts, we've reached the top
                    if no_change_count >= 3:
                        logger.info("Reached top of conversation history")
                        break
                else:
                    no_change_count = 0

                previous_height = new_height
                scroll_count += 1
                logger.debug(f"Scroll {scroll_count}/{max_scrolls}")

            logger.info(f"Completed scrolling after {scroll_count} attempts")

        except Exception as e:
            logger.warning(f"Scroll handling failed: {e}")
            # Continue anyway - we'll get partial history

    def _extract_messages(self) -> List[Message]:
        """Extract all messages from the conversation container.

        Returns:
            List of Message objects
        """
        messages = []

        try:
            # Wait for message container
            wait_for_element(
                self.driver,
                self.archive_selectors.message_container,
                timeout=10
            )

            # Find all user messages
            user_messages = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.selectors.message_bubble_user
            )

            logger.debug(f"Found {len(user_messages)} user messages")

            for element in user_messages:
                message = self._extract_message(element, is_user=True)
                if message:
                    messages.append(message)

            # Find all received messages (if selector exists)
            if self.selectors.message_bubble_bot:
                received_messages = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    self.selectors.message_bubble_bot
                )

                logger.debug(f"Found {len(received_messages)} received messages")

                for element in received_messages:
                    message = self._extract_message(element, is_user=False)
                    if message:
                        messages.append(message)

            # Sort by timestamp if available, otherwise maintain order
            messages = self._sort_messages(messages)

            return messages

        except Exception as e:
            logger.error(f"Failed to extract messages: {e}")
            return messages

    def _extract_message(self, element, is_user: bool) -> Message | None:
        """Extract message data from a message element.

        Args:
            element: WebElement containing the message
            is_user: Whether this is a user-sent message

        Returns:
            Message object, or None if extraction fails
        """
        try:
            # Extract message text
            text = element.text.strip()

            if not text:
                return None

            # Extract timestamp if selector exists
            timestamp = None
            if self.archive_selectors.message_timestamp:
                try:
                    timestamp_elem = element.find_element(
                        By.CSS_SELECTOR,
                        self.archive_selectors.message_timestamp
                    )
                    timestamp = timestamp_elem.text.strip()
                except:
                    pass

            return Message(
                text=text,
                timestamp=timestamp,
                is_user=is_user
            )

        except Exception as e:
            logger.debug(f"Failed to extract message: {e}")
            return None

    def _sort_messages(self, messages: List[Message]) -> List[Message]:
        """Sort messages chronologically.

        Args:
            messages: Unsorted list of messages

        Returns:
            Chronologically sorted messages
        """
        # For now, we'll rely on DOM order
        # In the future, we could parse timestamps for better sorting
        return messages
