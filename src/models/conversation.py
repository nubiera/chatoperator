"""Conversation and Message data models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Single message in a conversation."""

    sender: Literal["user", "bot"]
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class Conversation(BaseModel):
    """A chat conversation."""

    conversation_id: str
    platform: str
    messages: list[Message]
    has_unread: bool = False
    last_message_time: datetime = Field(default_factory=lambda: datetime.now())

    def get_history_text(self) -> str:
        """Get conversation history as formatted text."""
        lines = []
        for msg in self.messages:
            lines.append(f"{msg.sender.upper()}: {msg.text}")
        return "\n".join(lines)
