"""Session persistence for maintaining login across script runs."""

import logging
import pickle
from pathlib import Path
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages browser session persistence via cookies."""

    def __init__(self, session_dir: Path = Path(".sessions")):
        """Initialize SessionManager.

        Args:
            session_dir: Directory to store session files (default: .sessions/)
        """
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def get_session_file(self, platform_name: str) -> Path:
        """Get session file path for a platform.

        Args:
            platform_name: Name of the platform (e.g., "Tinder", "WhatsApp Web")

        Returns:
            Path to session pickle file
        """
        # Sanitize platform name for filename
        safe_name = platform_name.lower().replace(" ", "_").replace("/", "_")
        return self.session_dir / f"{safe_name}_cookies.pkl"

    def save_session(self, driver: WebDriver, platform_name: str) -> bool:
        """Save browser cookies to file.

        Args:
            driver: Selenium WebDriver instance
            platform_name: Name of the platform

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            session_file = self.get_session_file(platform_name)

            # Get all cookies from the browser
            cookies = driver.get_cookies()

            if not cookies:
                logger.warning(f"No cookies found for {platform_name}, skipping save")
                return False

            # Save cookies to file
            with open(session_file, "wb") as f:
                pickle.dump(cookies, f)

            logger.info(f"✓ Session saved for {platform_name} ({len(cookies)} cookies)")
            logger.debug(f"Session file: {session_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save session for {platform_name}: {e}")
            return False

    def load_session(self, driver: WebDriver, platform_name: str) -> bool:
        """Load browser cookies from file.

        Args:
            driver: Selenium WebDriver instance
            platform_name: Name of the platform

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            session_file = self.get_session_file(platform_name)

            # Check if session file exists
            if not session_file.exists():
                logger.debug(f"No saved session found for {platform_name}")
                return False

            # Load cookies from file
            with open(session_file, "rb") as f:
                cookies = pickle.load(f)

            if not cookies:
                logger.warning(f"Session file empty for {platform_name}")
                return False

            # Add cookies to browser
            for cookie in cookies:
                try:
                    # Remove expiry if present (can cause issues)
                    if "expiry" in cookie:
                        cookie["expiry"] = int(cookie["expiry"])

                    driver.add_cookie(cookie)
                except WebDriverException as e:
                    logger.debug(f"Could not add cookie {cookie.get('name')}: {e}")
                    continue

            logger.info(f"✓ Session loaded for {platform_name} ({len(cookies)} cookies)")
            logger.debug(f"Session file: {session_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to load session for {platform_name}: {e}")
            return False

    def delete_session(self, platform_name: str) -> bool:
        """Delete saved session for a platform.

        Args:
            platform_name: Name of the platform

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            session_file = self.get_session_file(platform_name)

            if session_file.exists():
                session_file.unlink()
                logger.info(f"✓ Session deleted for {platform_name}")
                return True
            else:
                logger.debug(f"No session file to delete for {platform_name}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete session for {platform_name}: {e}")
            return False

    def has_session(self, platform_name: str) -> bool:
        """Check if a saved session exists for a platform.

        Args:
            platform_name: Name of the platform

        Returns:
            True if session file exists, False otherwise
        """
        session_file = self.get_session_file(platform_name)
        return session_file.exists()

    def validate_session(
        self,
        driver: WebDriver,
        validation_selector: Optional[str] = None
    ) -> bool:
        """Validate that the loaded session is still active.

        Args:
            driver: Selenium WebDriver instance
            validation_selector: Optional CSS selector to check for logged-in state

        Returns:
            True if session appears valid, False otherwise
        """
        try:
            # Basic validation: check if we have cookies
            cookies = driver.get_cookies()
            if not cookies:
                logger.debug("Session validation failed: no cookies")
                return False

            # Optional: check for a specific element that only appears when logged in
            if validation_selector:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC

                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, validation_selector))
                    )
                    logger.debug("Session validation passed: found logged-in indicator")
                    return True
                except:
                    logger.debug("Session validation failed: logged-in indicator not found")
                    return False

            # If no validation selector, assume cookies mean we're logged in
            return True

        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False
