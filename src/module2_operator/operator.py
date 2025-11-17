"""Main operator orchestrator for Module 2."""

import time
from pathlib import Path

from src.config.settings import settings
from src.module2_operator.authenticator import Authenticator
from src.module2_operator.cache_loader import load_cache
from src.module2_operator.chatbot_interface import ChatbotInterface
from src.module2_operator.conversation_reader import ConversationReader
from src.module2_operator.message_sender import MessageSender
from src.module2_operator.polling_loop import PollingLoop
from src.module2_operator.round_robin import RoundRobinScheduler
from src.selenium_utils.driver_factory import create_driver
from src.utils.exceptions import (
    RecalibrationRequiredException,
    SelectorNotFoundException,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChatOperator:
    """Main operator for automated chat operations."""

    def __init__(self, platform_name: str, cache_dir: Path):
        """
        Initialize the operator.

        Args:
            platform_name: Name of the platform to operate on
            cache_dir: Cache directory containing platform configs
        """
        # Load configuration
        self.config = load_cache(platform_name, cache_dir)
        logger.info(f"Loaded configuration for {self.config.platform_name}")

        # Create driver (headless for production)
        self.driver = create_driver(
            headless=settings.HEADLESS_MODE, browser=settings.DEFAULT_BROWSER
        )

        # Initialize components
        self.authenticator = Authenticator(self.driver, self.config)
        self.reader = ConversationReader(self.driver, self.config)
        self.sender = MessageSender(self.driver, self.config)
        self.scheduler = RoundRobinScheduler()
        self.poller = PollingLoop(
            self.driver, self.config, self.scheduler, poll_interval=settings.POLL_INTERVAL
        )
        self.chatbot = ChatbotInterface()

        logger.info("ChatOperator initialized")

    def run(self, manual_login_wait: int = 60) -> None:
        """
        Main operation loop.

        Args:
            manual_login_wait: Seconds to wait for manual login (e.g., QR code)

        Raises:
            RecalibrationRequiredException: If selectors fail and recalibration needed
        """
        logger.info(f"Starting operator for {self.config.platform_name}")

        try:
            # Authenticate
            logger.info("Step 1: Authenticating...")
            self.authenticator.ensure_authenticated(manual_wait=manual_login_wait)

            # Main operation loop
            logger.info("Step 2: Starting main operation loop...")
            cycle_count = 0

            while True:
                try:
                    cycle_count += 1
                    logger.info(f"=== Cycle {cycle_count} ===")

                    # Poll for updates
                    unread_ids = self.poller.poll_for_updates()

                    if unread_ids:
                        self.scheduler.prioritize_unread(unread_ids)
                        logger.info(f"Prioritized {len(unread_ids)} unread conversations")

                    # Get next conversation to process
                    conv_id = self.scheduler.get_next_conversation()

                    if not conv_id:
                        logger.info(
                            f"No active conversations. Sleeping {self.poller.poll_interval}s..."
                        )
                        time.sleep(self.poller.poll_interval)
                        continue

                    # Process conversation
                    logger.info(f"Processing conversation: {conv_id}")

                    try:
                        self._process_conversation(conv_id)
                    except SelectorNotFoundException as e:
                        logger.error(f"Selector error: {e}")
                        raise RecalibrationRequiredException(
                            f"Selectors outdated for {self.config.platform_name}. "
                            f"Run Module 1 to recalibrate: "
                            f"uv run python scripts/analyze_platform.py "
                            f"'{self.config.platform_name}' {self.config.url}"
                        ) from e

                    # Small delay before next conversation
                    time.sleep(2)

                except KeyboardInterrupt:
                    logger.info("Operation interrupted by user")
                    break
                except RecalibrationRequiredException:
                    # Re-raise recalibration errors
                    raise
                except Exception as e:
                    logger.error(f"Error in main loop: {e}", exc_info=True)
                    logger.warning("Continuing after error...")
                    time.sleep(5)
                    continue

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            # Cleanup
            logger.info("Closing browser...")
            self.driver.quit()
            logger.info("Operator stopped")

    def _process_conversation(self, conversation_id: str) -> None:
        """
        Process a single conversation: read → chatbot → send.

        Args:
            conversation_id: Conversation identifier

        Raises:
            SelectorNotFoundException: If selectors fail
        """
        # Read conversation history
        conversation = self.reader.read_conversation(conversation_id)

        if not conversation.messages:
            logger.info("No messages in conversation, skipping...")
            return

        # Get chatbot response
        logger.info("Getting chatbot response...")
        response_text = self.chatbot.get_response(conversation)

        if not response_text:
            logger.warning("Empty chatbot response, skipping send")
            return

        # Send response
        logger.info(f"Sending response: {response_text[:100]}...")
        self.sender.send_message(response_text)

        logger.info(f"✅ Conversation {conversation_id} processed successfully")
