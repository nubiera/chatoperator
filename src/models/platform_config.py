"""Platform configuration data models."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class SelectorsModel(BaseModel):
    """CSS/XPath selectors for platform elements."""

    input_field: str = Field(..., description="Text input selector")
    send_button: str = Field(..., description="Send button selector")
    message_bubble_user: str = Field(..., description="User message bubble pattern")
    message_bubble_bot: str | None = Field(None, description="Bot message bubble pattern")
    conversation_list: str = Field(..., description="List of conversations/chats")
    unread_indicator: str = Field(..., description="Unread message indicator")


class WaitTimeoutsModel(BaseModel):
    """Timeout configurations in seconds."""

    page_load: int = Field(default=30, ge=5, le=120)
    element_visible: int = Field(default=10, ge=2, le=60)
    message_send: int = Field(default=5, ge=1, le=30)


class PlatformConfig(BaseModel):
    """Configuration cache for a chat platform."""

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}

    platform_name: str
    url: HttpUrl
    last_updated: datetime
    selectors: SelectorsModel
    wait_timeouts: WaitTimeoutsModel = Field(default_factory=WaitTimeoutsModel)
