"""Pytest configuration and shared fixtures."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from src.models.platform_config import (
    PlatformConfig,
    SelectorsModel,
    WaitTimeoutsModel,
)


@pytest.fixture
def sample_selectors() -> SelectorsModel:
    """Sample selectors for testing."""
    return SelectorsModel(
        input_field="textarea#message-input",
        send_button="button[aria-label='Send']",
        message_bubble_user="div.message-out",
        message_bubble_bot="div.message-in",
        conversation_list="div.conversations-list",
        unread_indicator="span.unread-badge",
    )


@pytest.fixture
def sample_config(sample_selectors: SelectorsModel) -> PlatformConfig:
    """Sample platform configuration for testing."""
    return PlatformConfig(
        platform_name="Test Platform",
        url="https://test.example.com",
        last_updated=datetime(2025, 1, 1, 12, 0, 0),
        selectors=sample_selectors,
        wait_timeouts=WaitTimeoutsModel(),
    )


@pytest.fixture
def sample_config_dict(sample_config: PlatformConfig) -> dict:
    """Sample config as dictionary."""
    return sample_config.model_dump(mode="json")


@pytest.fixture
def mock_driver() -> Mock:
    """Mock Selenium WebDriver."""
    driver = Mock(spec=WebDriver)
    driver.get = Mock()
    driver.quit = Mock()
    driver.find_element = Mock()
    driver.find_elements = Mock(return_value=[])
    driver.execute_script = Mock(return_value="complete")
    driver.page_source = "<html><body>Test</body></html>"
    return driver


@pytest.fixture
def mock_gemini_response() -> str:
    """Mock Gemini API response with selectors."""
    return json.dumps(
        {
            "input_field": "textarea#input",
            "send_button": "button.send",
            "message_bubble_user": "div.msg-out",
            "message_bubble_bot": "div.msg-in",
            "conversation_list": "div.conv-list",
            "unread_indicator": "span.unread",
        }
    )


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Temporary cache directory for testing."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def sample_cache_file(temp_cache_dir: Path, sample_config: PlatformConfig) -> Path:
    """Create a sample cache file for testing."""
    cache_file = temp_cache_dir / "test_platform.json"

    with open(cache_file, "w") as f:
        json.dump(sample_config.model_dump(mode="json"), f, indent=2)

    return cache_file
