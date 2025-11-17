"""Extract user profile information from chat platforms."""

import logging
from typing import Dict, Any

from pydantic import BaseModel
from selenium.webdriver.remote.webdriver import WebDriver

from src.models.platform_config import ArchiveSelectorsModel
from src.selenium_utils.wait_helpers import wait_for_element
from src.utils.exceptions import ChatOperatorException

logger = logging.getLogger(__name__)


class ProfileExtractionException(ChatOperatorException):
    """Exception raised when profile extraction fails."""
    pass


class UserProfile(BaseModel):
    """User profile data model."""

    name: str
    bio: str | None = None
    age: str | None = None
    distance: str | None = None
    additional_info: Dict[str, Any] = {}


class ProfileExtractor:
    """Extracts user profile information from web pages."""

    def __init__(self, driver: WebDriver, selectors: ArchiveSelectorsModel):
        """Initialize ProfileExtractor.

        Args:
            driver: Selenium WebDriver instance
            selectors: Archive-specific CSS/XPath selectors
        """
        self.driver = driver
        self.selectors = selectors

    def extract_profile(self, timeout: int = 10) -> UserProfile:
        """Extract profile information from the current page.

        Args:
            timeout: Seconds to wait for profile elements

        Returns:
            UserProfile with extracted data

        Raises:
            ProfileExtractionException: If profile extraction fails
        """
        try:
            # Extract name (required)
            name = self._extract_text(self.selectors.profile_name, timeout)

            if not name:
                raise ProfileExtractionException("Failed to extract profile name")

            # Extract optional fields
            bio = None
            if self.selectors.profile_bio:
                bio = self._extract_text(self.selectors.profile_bio, timeout)

            age = None
            if self.selectors.profile_age:
                age = self._extract_text(self.selectors.profile_age, timeout)

            distance = None
            if self.selectors.profile_distance:
                distance = self._extract_text(self.selectors.profile_distance, timeout)

            logger.info(f"Extracted profile for: {name}")

            return UserProfile(
                name=name,
                bio=bio,
                age=age,
                distance=distance
            )

        except Exception as e:
            logger.error(f"Failed to extract profile: {e}")
            raise ProfileExtractionException(f"Profile extraction failed: {e}")

    def _extract_text(self, selector: str, timeout: int) -> str | None:
        """Extract text from an element.

        Args:
            selector: CSS selector for the element
            timeout: Seconds to wait for element

        Returns:
            Extracted text, or None if element not found
        """
        try:
            element = wait_for_element(self.driver, selector, timeout)
            text = element.text.strip()

            if not text:
                # Try value attribute if text is empty
                text = element.get_attribute("value")

            return text if text else None

        except Exception as e:
            logger.debug(f"Could not extract text from {selector}: {e}")
            return None
