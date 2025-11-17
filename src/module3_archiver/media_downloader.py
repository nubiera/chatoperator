"""Download profile pictures and media from conversations."""

import logging
from pathlib import Path
from typing import List

import requests
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.selenium_utils.wait_helpers import wait_for_element
from src.utils.exceptions import ChatOperatorException

logger = logging.getLogger(__name__)


class MediaDownloadException(ChatOperatorException):
    """Exception raised when media download fails."""
    pass


class MediaDownloader:
    """Downloads profile pictures and other media."""

    def __init__(self, driver: WebDriver, download_dir: Path):
        """Initialize MediaDownloader.

        Args:
            driver: Selenium WebDriver instance
            download_dir: Directory to save downloaded media
        """
        self.driver = driver
        self.download_dir = download_dir
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def download_profile_picture(
        self,
        selector: str,
        output_path: Path,
        timeout: int = 10
    ) -> Path | None:
        """Download a single profile picture.

        Args:
            selector: CSS selector for the profile picture element
            output_path: Path where the image should be saved
            timeout: Seconds to wait for element

        Returns:
            Path to downloaded file, or None if download failed

        Raises:
            MediaDownloadException: If download fails
        """
        try:
            # Find the profile picture element
            img_element = wait_for_element(self.driver, selector, timeout)

            # Extract image URL from src or background-image
            img_url = self._extract_image_url(img_element)

            if not img_url:
                logger.warning(f"No image URL found for selector: {selector}")
                return None

            # Download the image
            return self._download_image(img_url, output_path)

        except Exception as e:
            logger.error(f"Failed to download profile picture: {e}")
            raise MediaDownloadException(f"Profile picture download failed: {e}")

    def download_all_profile_pictures(
        self,
        selector: str,
        output_dir: Path,
        timeout: int = 10
    ) -> List[Path]:
        """Download all profile pictures from a gallery.

        Args:
            selector: CSS selector for profile picture elements
            output_dir: Directory to save images
            timeout: Seconds to wait for elements

        Returns:
            List of paths to downloaded files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        downloaded_files = []

        try:
            # Find all image elements
            images = self.driver.find_elements(By.CSS_SELECTOR, selector)

            logger.info(f"Found {len(images)} profile pictures to download")

            for idx, img_element in enumerate(images, start=1):
                try:
                    img_url = self._extract_image_url(img_element)

                    if not img_url:
                        logger.warning(f"No URL for image {idx}")
                        continue

                    output_path = output_dir / f"profile_picture_{idx}.jpg"
                    downloaded_path = self._download_image(img_url, output_path)

                    if downloaded_path:
                        downloaded_files.append(downloaded_path)
                        logger.debug(f"Downloaded image {idx} to {downloaded_path}")

                except Exception as e:
                    logger.warning(f"Failed to download image {idx}: {e}")
                    continue

            logger.info(f"Downloaded {len(downloaded_files)} profile pictures")
            return downloaded_files

        except Exception as e:
            logger.error(f"Failed to download profile pictures: {e}")
            raise MediaDownloadException(f"Gallery download failed: {e}")

    def _extract_image_url(self, element) -> str | None:
        """Extract image URL from an element.

        Args:
            element: WebElement containing the image

        Returns:
            Image URL string, or None if not found
        """
        # Try src attribute first
        img_url = element.get_attribute("src")

        if img_url and img_url.startswith("http"):
            return img_url

        # Try background-image CSS property
        background = element.value_of_css_property("background-image")

        if background and background != "none":
            # Extract URL from url("...") or url('...')
            if "url(" in background:
                img_url = background.split("url(")[1].split(")")[0].strip("\"'")
                if img_url.startswith("http"):
                    return img_url

        # Try data-src attribute (lazy loading)
        data_src = element.get_attribute("data-src")
        if data_src and data_src.startswith("http"):
            return data_src

        return None

    def _download_image(self, url: str, output_path: Path) -> Path | None:
        """Download image from URL to file.

        Args:
            url: Image URL
            output_path: Where to save the file

        Returns:
            Path to downloaded file, or None if failed
        """
        try:
            logger.debug(f"Downloading image from {url}")

            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Write to file
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.debug(f"Saved image to {output_path}")
            return output_path

        except requests.RequestException as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None
