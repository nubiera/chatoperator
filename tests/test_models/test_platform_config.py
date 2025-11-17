"""Tests for platform configuration models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models.platform_config import (
    PlatformConfig,
    SelectorsModel,
    WaitTimeoutsModel,
)


class TestSelectorsModel:
    """Tests for SelectorsModel."""

    def test_valid_selectors(self) -> None:
        """Test creating valid selectors."""
        selectors = SelectorsModel(
            input_field="textarea#input",
            send_button="button.send",
            message_bubble_user="div.msg-out",
            message_bubble_bot="div.msg-in",
            conversation_list="div.conv-list",
            unread_indicator="span.unread",
        )

        assert selectors.input_field == "textarea#input"
        assert selectors.send_button == "button.send"

    def test_optional_bot_selector(self) -> None:
        """Test that message_bubble_bot is optional."""
        selectors = SelectorsModel(
            input_field="textarea#input",
            send_button="button.send",
            message_bubble_user="div.msg-out",
            message_bubble_bot=None,
            conversation_list="div.conv-list",
            unread_indicator="span.unread",
        )

        assert selectors.message_bubble_bot is None

    def test_missing_required_field(self) -> None:
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError):
            SelectorsModel(
                input_field="textarea#input",
                # Missing send_button
                message_bubble_user="div.msg-out",
                conversation_list="div.conv-list",
                unread_indicator="span.unread",
            )


class TestWaitTimeoutsModel:
    """Tests for WaitTimeoutsModel."""

    def test_default_timeouts(self) -> None:
        """Test default timeout values."""
        timeouts = WaitTimeoutsModel()

        assert timeouts.page_load == 30
        assert timeouts.element_visible == 10
        assert timeouts.message_send == 5

    def test_custom_timeouts(self) -> None:
        """Test custom timeout values."""
        timeouts = WaitTimeoutsModel(page_load=60, element_visible=20, message_send=10)

        assert timeouts.page_load == 60
        assert timeouts.element_visible == 20
        assert timeouts.message_send == 10

    def test_timeout_validation(self) -> None:
        """Test that timeouts are validated within ranges."""
        # Too small
        with pytest.raises(ValidationError):
            WaitTimeoutsModel(page_load=2)  # Min is 5

        # Too large
        with pytest.raises(ValidationError):
            WaitTimeoutsModel(page_load=200)  # Max is 120


class TestPlatformConfig:
    """Tests for PlatformConfig."""

    def test_valid_config(self, sample_selectors: SelectorsModel) -> None:
        """Test creating valid platform config."""
        config = PlatformConfig(
            platform_name="Test Platform",
            url="https://test.example.com",
            last_updated=datetime.now(),
            selectors=sample_selectors,
            wait_timeouts=WaitTimeoutsModel(),
        )

        assert config.platform_name == "Test Platform"
        assert str(config.url) == "https://test.example.com/"

    def test_config_serialization(self, sample_config: PlatformConfig) -> None:
        """Test config can be serialized to dict."""
        config_dict = sample_config.model_dump(mode="json")

        assert config_dict["platform_name"] == "Test Platform"
        assert "selectors" in config_dict
        assert "wait_timeouts" in config_dict
