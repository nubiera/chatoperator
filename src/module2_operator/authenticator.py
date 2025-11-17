"""Authentication handler for chat platforms."""

import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver

from src.models.platform_config import PlatformConfig
from src.selenium_utils.wait_helpers import wait_for_element
from src.utils.exceptions import AuthenticationFailedException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Authenticator:
    """Handles authentication to chat platforms."""

    def __init__(self, driver: WebDriver, config: PlatformConfig):
        """
        Initialize authenticator.

        Args:
            driver: WebDriver instance
            config: Platform configuration
        """
        self.driver = driver
        self.config = config

    def ensure_authenticated(
        self, credentials: dict[str, str] | None = None, manual_wait: int = 60
    ) -> None:
        """
        Ensure the user is authenticated to the platform.

        Args:
            credentials: Optional dict with username/password (platform-specific)
            manual_wait: Seconds to wait for manual login (e.g., QR code scan)

        Raises:
            AuthenticationFailedException: If authentication fails
        """
        logger.info(f"Ensuring authentication for {self.config.platform_name}...")

        # Navigate to platform
        self.driver.get(str(self.config.url))
        time.sleep(3)  # Wait for redirect/load

        # Check if already logged in
        if self._is_logged_in():
            logger.info("✅ Already authenticated")
            return

        # Try automatic login if credentials provided
        if credentials:
            logger.info("Attempting automatic login...")
            self._perform_login(credentials)

            if self._is_logged_in():
                logger.info("✅ Automatic login successful")
                return

        # Fall back to manual login
        logger.warning(
            f"⏳ Manual login required (e.g., QR code scan). "
            f"Waiting {manual_wait} seconds..."
        )
        logger.warning("Please complete the login process in the browser window.")

        time.sleep(manual_wait)

        # Check again after manual wait
        if not self._is_logged_in():
            logger.error("❌ Authentication failed or timed out")
            raise AuthenticationFailedException(
                f"Failed to authenticate to {self.config.platform_name}. "
                f"Please check the browser window and try again."
            )

        logger.info("✅ Manual login successful")

    def _is_logged_in(self) -> bool:
        """
        Check if user is logged in by looking for main interface elements.

        Returns:
            True if logged in
        """
        try:
            # Check for presence of conversation list (main interface indicator)
            wait_for_element(
                self.driver,
                self.config.selectors.conversation_list,
                timeout=5,
            )
            logger.debug("Login check: Conversation list found - user is logged in")
            return True
        except TimeoutException:
            logger.debug("Login check: Conversation list not found - not logged in")
            return False

    def _perform_login(self, credentials: dict[str, str]) -> None:
        """
        Perform automatic login (platform-specific).

        This is a placeholder implementation. Real implementation would need
        platform-specific login flows (username/password fields, buttons, etc.)

        Args:
            credentials: Dictionary with login credentials
        """
        logger.warning(
            "Automatic login not implemented for this platform. "
            "Please implement platform-specific login logic."
        )

        # Example implementation (would need platform-specific selectors):
        # try:
        #     username_field = wait_for_element(driver, "#username")
        #     password_field = wait_for_element(driver, "#password")
        #     login_button = wait_for_element(driver, "#login-button")
        #
        #     username_field.send_keys(credentials.get("username", ""))
        #     password_field.send_keys(credentials.get("password", ""))
        #     login_button.click()
        #
        #     time.sleep(3)  # Wait for login to complete
        # except Exception as e:
        #     logger.error(f"Automatic login failed: {e}")

        pass
