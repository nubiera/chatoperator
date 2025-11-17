"""Main archiver orchestrator for downloading conversations."""

import logging
from pathlib import Path
from typing import List

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.models.platform_config import PlatformConfig
from src.module3_archiver.profile_extractor import ProfileExtractor
from src.module3_archiver.media_downloader import MediaDownloader
from src.module3_archiver.conversation_downloader import ConversationDownloader
from src.module3_archiver.markdown_exporter import MarkdownExporter
from src.selenium_utils.wait_helpers import wait_for_element
from src.utils.exceptions import ChatOperatorException

logger = logging.getLogger(__name__)


class ArchiverException(ChatOperatorException):
    """Exception raised when archiver operation fails."""
    pass


class ConversationArchiver:
    """Orchestrates the full conversation archival process."""

    def __init__(
        self,
        driver: WebDriver,
        config: PlatformConfig,
        output_dir: Path
    ):
        """Initialize ConversationArchiver.

        Args:
            driver: Selenium WebDriver instance
            config: Platform configuration with selectors
            output_dir: Base directory for archived conversations

        Raises:
            ArchiverException: If archive selectors not configured
        """
        if not config.archive_selectors:
            raise ArchiverException(
                "Platform config missing archive_selectors. "
                "Run analyzer with --archive flag to generate them."
            )

        self.driver = driver
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.profile_extractor = ProfileExtractor(
            driver,
            config.archive_selectors
        )
        self.media_downloader = MediaDownloader(driver, output_dir)
        self.conversation_downloader = ConversationDownloader(
            driver,
            config.selectors,
            config.archive_selectors
        )
        self.markdown_exporter = MarkdownExporter()

    def archive_all_conversations(
        self,
        max_conversations: int | None = None
    ) -> int:
        """Archive all conversations from the platform.

        Args:
            max_conversations: Optional limit on number of conversations to archive

        Returns:
            Number of successfully archived conversations

        Raises:
            ArchiverException: If archival process fails
        """
        try:
            logger.info("Starting full conversation archive")

            # Get list of all conversations
            conversation_elements = self._get_conversation_list()

            total = len(conversation_elements)
            if max_conversations:
                total = min(total, max_conversations)
                conversation_elements = conversation_elements[:max_conversations]

            logger.info(f"Found {total} conversations to archive")

            archived_count = 0

            for idx, conv_element in enumerate(conversation_elements, start=1):
                try:
                    logger.info(f"\n=== Archiving conversation {idx}/{total} ===")

                    # Click to open conversation
                    conv_element.click()

                    # Wait for conversation to load
                    wait_for_element(
                        self.driver,
                        self.config.archive_selectors.message_container,
                        timeout=10
                    )

                    # Archive this conversation
                    success = self._archive_single_conversation()

                    if success:
                        archived_count += 1

                    logger.info(f"Progress: {archived_count}/{idx} successful")

                except Exception as e:
                    logger.error(f"Failed to archive conversation {idx}: {e}")
                    continue

            logger.info(f"\n=== Archive Complete ===")
            logger.info(f"Successfully archived: {archived_count}/{total}")

            return archived_count

        except Exception as e:
            logger.error(f"Archive process failed: {e}")
            raise ArchiverException(f"Failed to archive conversations: {e}")

    def archive_current_conversation(self) -> bool:
        """Archive the currently open conversation.

        Returns:
            True if successful, False otherwise

        Raises:
            ArchiverException: If archival fails
        """
        logger.info("Archiving current conversation")
        return self._archive_single_conversation()

    def _archive_single_conversation(self) -> bool:
        """Archive a single conversation.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract profile information
            logger.info("Extracting profile information...")
            profile = self.profile_extractor.extract_profile()

            # Create conversation directory
            safe_name = self._sanitize_filename(profile.name)
            conv_dir = self.output_dir / safe_name
            conv_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Saving to: {conv_dir}")

            # Download profile picture(s)
            logger.info("Downloading profile pictures...")
            profile_pictures = self._download_profile_pictures(conv_dir)

            # Download conversation history
            logger.info("Downloading conversation history...")
            messages = self.conversation_downloader.download_conversation()

            # Export to markdown
            logger.info("Exporting to markdown...")
            markdown_path = conv_dir / "conversation.md"
            self.markdown_exporter.export_conversation(
                profile,
                messages,
                markdown_path,
                profile_pictures
            )

            # Export profile metadata as JSON
            profile_path = conv_dir / "profile.json"
            self.markdown_exporter.export_profile_metadata(profile, profile_path)

            logger.info(f"✓ Successfully archived conversation with {profile.name}")
            logger.info(f"  - {len(messages)} messages")
            logger.info(f"  - {len(profile_pictures)} profile pictures")

            return True

        except Exception as e:
            logger.error(f"Failed to archive conversation: {e}")
            return False

    def _get_conversation_list(self) -> List:
        """Get list of all conversation elements.

        Returns:
            List of WebElements for conversations

        Raises:
            ArchiverException: If conversation list cannot be found
        """
        try:
            # Wait for conversation list to load
            wait_for_element(
                self.driver,
                self.config.selectors.conversation_list,
                timeout=15
            )

            # Find all conversation items
            conversations = self.driver.find_elements(
                By.CSS_SELECTOR,
                self.config.archive_selectors.conversation_item
            )

            if not conversations:
                raise ArchiverException("No conversations found")

            logger.info(f"Found {len(conversations)} conversations")
            return conversations

        except Exception as e:
            logger.error(f"Failed to get conversation list: {e}")
            raise ArchiverException(f"Could not find conversations: {e}")

    def _download_profile_pictures(self, output_dir: Path) -> List[Path]:
        """Download all profile pictures for the current conversation.

        Args:
            output_dir: Directory to save pictures

        Returns:
            List of downloaded picture paths
        """
        try:
            # Try to download all profile pictures if selector exists
            if self.config.archive_selectors.all_profile_pictures:
                return self.media_downloader.download_all_profile_pictures(
                    self.config.archive_selectors.all_profile_pictures,
                    output_dir
                )

            # Otherwise, download just the main profile picture
            main_pic = self.media_downloader.download_profile_picture(
                self.config.archive_selectors.profile_picture,
                output_dir / "profile_picture.jpg"
            )

            return [main_pic] if main_pic else []

        except Exception as e:
            logger.warning(f"Failed to download profile pictures: {e}")
            return []

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a name for use as a directory name.

        Args:
            name: Original name

        Returns:
            Sanitized name safe for filesystem
        """
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        sanitized = name

        for char in invalid_chars:
            sanitized = sanitized.replace(char, "_")

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(". ")

        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]

        return sanitized or "unknown"
