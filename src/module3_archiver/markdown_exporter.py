"""Export conversations to Markdown format."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

from src.module3_archiver.conversation_downloader import Message
from src.module3_archiver.profile_extractor import UserProfile
from src.utils.exceptions import ChatOperatorException

logger = logging.getLogger(__name__)


class MarkdownExportException(ChatOperatorException):
    """Exception raised when markdown export fails."""
    pass


class MarkdownExporter:
    """Exports conversation data to Markdown format."""

    def export_conversation(
        self,
        profile: UserProfile,
        messages: List[Message],
        output_path: Path,
        profile_pictures: List[Path] | None = None
    ):
        """Export conversation to Markdown file.

        Args:
            profile: User profile information
            messages: List of conversation messages
            output_path: Path where markdown file should be saved
            profile_pictures: Optional list of profile picture paths

        Raises:
            MarkdownExportException: If export fails
        """
        try:
            logger.info(f"Exporting conversation to {output_path}")

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build markdown content
            content = self._build_markdown(profile, messages, profile_pictures)

            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Successfully exported {len(messages)} messages to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export markdown: {e}")
            raise MarkdownExportException(f"Markdown export failed: {e}")

    def _build_markdown(
        self,
        profile: UserProfile,
        messages: List[Message],
        profile_pictures: List[Path] | None
    ) -> str:
        """Build markdown content from conversation data.

        Args:
            profile: User profile information
            messages: List of messages
            profile_pictures: Optional profile picture paths

        Returns:
            Formatted markdown string
        """
        lines = []

        # Header
        lines.append(f"# Conversation with {profile.name}\n")

        # Profile information
        lines.append("## Profile Information\n")
        lines.append(f"**Name:** {profile.name}\n")

        if profile.age:
            lines.append(f"**Age:** {profile.age}\n")

        if profile.distance:
            lines.append(f"**Distance:** {profile.distance}\n")

        if profile.bio:
            lines.append(f"**Bio:** {profile.bio}\n")

        # Profile pictures
        if profile_pictures:
            lines.append("\n### Profile Pictures\n")
            for idx, pic_path in enumerate(profile_pictures, start=1):
                # Use relative path from markdown file
                rel_path = pic_path.name
                lines.append(f"![Profile Picture {idx}]({rel_path})\n")

        # Metadata
        lines.append(f"\n**Exported:** {datetime.now().isoformat()}\n")
        lines.append(f"**Total Messages:** {len(messages)}\n")

        # Conversation
        lines.append("\n---\n")
        lines.append("\n## Conversation\n")

        for message in messages:
            lines.append(self._format_message(message))
            lines.append("\n")

        return "".join(lines)

    def _format_message(self, message: Message) -> str:
        """Format a single message as markdown.

        Args:
            message: Message to format

        Returns:
            Formatted markdown string
        """
        # Determine sender indicator
        if message.is_user:
            sender = "**You**"
        else:
            sender = "**Them**"

        # Include timestamp if available
        if message.timestamp:
            header = f"{sender} _{message.timestamp}_"
        else:
            header = sender

        # Format with blockquote for visual separation
        return f"{header}\n> {message.text}\n"

    def export_profile_metadata(
        self,
        profile: UserProfile,
        output_path: Path
    ):
        """Export profile information as JSON.

        Args:
            profile: User profile information
            output_path: Path where JSON should be saved

        Raises:
            MarkdownExportException: If export fails
        """
        try:
            logger.info(f"Exporting profile metadata to {output_path}")

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(profile.model_dump_json(indent=2))

            logger.info(f"Successfully exported profile to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export profile metadata: {e}")
            raise MarkdownExportException(f"Profile export failed: {e}")
