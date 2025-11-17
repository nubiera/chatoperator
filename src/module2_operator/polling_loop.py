"""Polling loop for detecting new conversations and messages."""


from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from src.config.settings import settings
from src.models.platform_config import PlatformConfig
from src.module2_operator.round_robin import RoundRobinScheduler
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class PollingLoop:
    """Periodically polls for new messages and conversations."""

    def __init__(
        self,
        driver: WebDriver,
        config: PlatformConfig,
        scheduler: RoundRobinScheduler,
        poll_interval: int = settings.POLL_INTERVAL,
    ):
        """
        Initialize polling loop.

        Args:
            driver: WebDriver instance
            config: Platform configuration
            scheduler: Round-robin scheduler
            poll_interval: Polling interval in seconds
        """
        self.driver = driver
        self.config = config
        self.scheduler = scheduler
        self.poll_interval = poll_interval

    def poll_for_updates(self) -> list[str]:
        """
        Poll for new messages and conversations.

        Returns:
            List of conversation IDs with unread messages
        """
        logger.debug("Polling for updates...")

        unread_conversations: list[str] = []

        try:
            # Find all conversation elements
            conversation_elements = self.driver.find_elements(
                By.CSS_SELECTOR, self.config.selectors.conversation_list
            )

            if not conversation_elements:
                logger.warning("No conversation elements found")
                return unread_conversations

            # Check each conversation for unread indicator
            for idx, conv_elem in enumerate(conversation_elements):
                try:
                    has_unread = self._has_unread_indicator(conv_elem)

                    if has_unread:
                        # Use index as conversation ID (simple approach)
                        # In real implementation, would extract actual conversation ID
                        conv_id = f"conv_{idx}"
                        unread_conversations.append(conv_id)
                        self.scheduler.add_conversation(conv_id)

                except Exception as e:
                    logger.debug(f"Error checking conversation {idx}: {e}")
                    continue

            if unread_conversations:
                logger.info(f"Found {len(unread_conversations)} conversations with unread messages")
            else:
                logger.debug("No unread messages found")

            return unread_conversations

        except Exception as e:
            logger.error(f"Polling error: {e}")
            return []

    def _has_unread_indicator(self, conv_element: WebElement) -> bool:
        """
        Check if conversation element has unread indicator.

        Args:
            conv_element: Conversation element

        Returns:
            True if unread indicator present
        """
        try:
            # Look for unread indicator within this conversation element
            conv_element.find_element(
                By.CSS_SELECTOR, self.config.selectors.unread_indicator
            )
            return True
        except NoSuchElementException:
            return False

    def _extract_conversation_id(self, conv_element: WebElement) -> str:
        """
        Extract conversation ID from element.

        This is a placeholder - real implementation would extract
        actual conversation ID from element attributes or data.

        Args:
            conv_element: Conversation element

        Returns:
            Conversation ID
        """
        try:
            # Try to get data-id or similar attribute
            conv_id = conv_element.get_attribute("data-id")
            if conv_id:
                return conv_id

            # Fallback: use element text or other identifier
            conv_id = conv_element.text[:50]  # First 50 chars
            return conv_id

        except Exception:
            # Ultimate fallback: use element location
            location = conv_element.location
            return f"conv_{location['x']}_{location['y']}"
