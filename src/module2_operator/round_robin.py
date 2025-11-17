"""Round-robin scheduler for conversation management."""


from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RoundRobinScheduler:
    """Manages round-robin scheduling of conversations."""

    def __init__(self) -> None:
        """Initialize the scheduler."""
        self.conversation_queue: list[str] = []
        self.current_index: int = 0

    def add_conversation(self, conversation_id: str) -> None:
        """
        Add a conversation to the queue.

        Args:
            conversation_id: Conversation identifier
        """
        if conversation_id not in self.conversation_queue:
            self.conversation_queue.append(conversation_id)
            logger.info(f"Added conversation to queue: {conversation_id}")

    def remove_conversation(self, conversation_id: str) -> None:
        """
        Remove a conversation from the queue.

        Args:
            conversation_id: Conversation identifier
        """
        if conversation_id in self.conversation_queue:
            self.conversation_queue.remove(conversation_id)
            # Reset index if it's out of bounds
            if self.current_index >= len(self.conversation_queue):
                self.current_index = 0
            logger.info(f"Removed conversation from queue: {conversation_id}")

    def get_next_conversation(self) -> str | None:
        """
        Get the next conversation in round-robin order.

        Returns:
            Conversation ID or None if queue is empty
        """
        if not self.conversation_queue:
            return None

        # Get current conversation
        conversation_id = self.conversation_queue[self.current_index]

        # Move to next index (circular)
        self.current_index = (self.current_index + 1) % len(self.conversation_queue)

        logger.debug(f"Next conversation: {conversation_id}")
        return conversation_id

    def prioritize_unread(self, unread_ids: list[str]) -> None:
        """
        Move unread conversations to the front of the queue.

        Args:
            unread_ids: List of conversation IDs with unread messages
        """
        for conv_id in unread_ids:
            if conv_id in self.conversation_queue:
                # Remove from current position
                self.conversation_queue.remove(conv_id)
                # Add to front
                self.conversation_queue.insert(0, conv_id)

        logger.info(f"Prioritized {len(unread_ids)} unread conversations")

    def get_queue_status(self) -> dict:
        """
        Get current queue status.

        Returns:
            Dictionary with queue information
        """
        return {
            "queue_length": len(self.conversation_queue),
            "current_index": self.current_index,
            "conversations": self.conversation_queue.copy(),
        }
