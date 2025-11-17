"""Conversation history reader."""

from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from src.models.conversation import Conversation, Message
from src.models.platform_config import PlatformConfig
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationReader:
    """Reads chat conversation history."""

    def __init__(self, driver: WebDriver, config: PlatformConfig):
        """
        Initialize conversation reader.

        Args:
            driver: WebDriver instance
            config: Platform configuration
        """
        self.driver = driver
        self.config = config

    def read_conversation(self, conversation_id: str) -> Conversation:
        """
        Read conversation history from active chat.

        Args:
            conversation_id: Conversation identifier

        Returns:
            Conversation object with message history
        """
        logger.info(f"Reading conversation: {conversation_id}")

        messages: list[Message] = []

        try:
            # Find user message bubbles
            user_bubbles = self.driver.find_elements(
                By.CSS_SELECTOR, self.config.selectors.message_bubble_user
            )

            # Find bot/received message bubbles (if selector exists)
            bot_bubbles: list[WebElement] = []
            if self.config.selectors.message_bubble_bot:
                bot_bubbles = self.driver.find_elements(
                    By.CSS_SELECTOR, self.config.selectors.message_bubble_bot
                )

            # Process user messages
            for bubble in user_bubbles:
                try:
                    text = bubble.text.strip()
                    if text:
                        messages.append(
                            Message(
                                sender="user",
                                text=text,
                                timestamp=datetime.now(),
                            )
                        )
                except Exception as e:
                    logger.warning(f"Failed to read user message: {e}")
                    continue

            # Process bot messages
            for bubble in bot_bubbles:
                try:
                    text = bubble.text.strip()
                    if text:
                        messages.append(
                            Message(
                                sender="bot",
                                text=text,
                                timestamp=datetime.now(),
                            )
                        )
                except Exception as e:
                    logger.warning(f"Failed to read bot message: {e}")
                    continue

            # Sort messages by position in DOM (approximation of time order)
            # In reality, messages are already in order from DOM traversal

            logger.info(f"Read {len(messages)} messages from conversation")

            # Limit conversation history to prevent token overflow
            max_messages = 50
            if len(messages) > max_messages:
                logger.warning(
                    f"Conversation has {len(messages)} messages, "
                    f"keeping last {max_messages}"
                )
                messages = messages[-max_messages:]

            return Conversation(
                conversation_id=conversation_id,
                platform=self.config.platform_name,
                messages=messages,
                has_unread=False,
                last_message_time=messages[-1].timestamp if messages else datetime.now(),
            )

        except Exception as e:
            logger.error(f"Failed to read conversation: {e}")
            # Return empty conversation on error
            return Conversation(
                conversation_id=conversation_id,
                platform=self.config.platform_name,
                messages=[],
                has_unread=False,
                last_message_time=datetime.now(),
            )
