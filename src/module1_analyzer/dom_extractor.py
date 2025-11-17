"""DOM/HTML extraction functionality."""

from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import WebDriver

from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def extract_dom(driver: WebDriver, focus_selector: str = "body") -> str:
    """
    Extract HTML/DOM structure from page.

    Args:
        driver: WebDriver instance
        focus_selector: CSS selector to focus extraction (default: "body")

    Returns:
        HTML string
    """
    logger.info("Extracting DOM structure...")

    # Get full page source
    html = driver.page_source

    # Optional: Parse and extract focused section
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Try to find focused section
        if focus_selector != "body":
            focused_element = soup.select_one(focus_selector)
            if focused_element:
                html = str(focused_element)
                logger.info(f"Extracted focused section: {focus_selector}")
            else:
                logger.warning(
                    f"Focus selector '{focus_selector}' not found, using full body"
                )
        else:
            # Use full HTML
            html = str(soup)

    except Exception as e:
        logger.warning(f"Failed to parse HTML with BeautifulSoup: {e}. Using raw HTML.")
        # Fall back to raw HTML
        pass

    logger.info(f"DOM extracted ({len(html)} characters)")
    return html


def clean_html(html: str, max_length: int = 100000) -> str:
    """
    Clean and minify HTML to reduce size.

    Args:
        html: Raw HTML string
        max_length: Maximum length to keep (default: 100000)

    Returns:
        Cleaned HTML string
    """
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style tags
        for tag in soup(["script", "style"]):
            tag.decompose()

        # Get text
        cleaned = str(soup)

        # Truncate if too long
        if len(cleaned) > max_length:
            logger.warning(
                f"HTML too long ({len(cleaned)} chars), truncating to {max_length}"
            )
            cleaned = cleaned[:max_length] + "\n... [truncated]"

        return cleaned

    except Exception as e:
        logger.error(f"Failed to clean HTML: {e}")
        # Return truncated original if cleaning fails
        if len(html) > max_length:
            return html[:max_length] + "\n... [truncated]"
        return html
