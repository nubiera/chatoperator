"""Gemini Vision API client for interface analysis."""

import json

from google import genai
from google.genai import types

from src.module1_analyzer.selector_generator import build_analysis_prompt
from src.utils.exceptions import GeminiAPIException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GeminiClient:
    """Client for Google Gemini Vision API."""

    def __init__(self, api_key: str):
        """
        Initialize Gemini client.

        Args:
            api_key: Google Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    def analyze_interface(
        self, screenshot_bytes: bytes, html_content: str, platform_name: str, include_archive: bool = False
    ) -> dict[str, str] | dict:
        """
        Analyze chat interface using vision + HTML.

        Args:
            screenshot_bytes: PNG screenshot bytes
            html_content: HTML/DOM structure
            platform_name: Name of the platform
            include_archive: Whether to extract archive selectors

        Returns:
            Dictionary mapping selector names to CSS selectors (old format)
            OR dictionary with "selectors" and "archive_selectors" keys (archive format)

        Raises:
            GeminiAPIException: If API call fails
        """
        logger.info(f"Analyzing interface for platform: {platform_name}")

        try:
            # Build prompt
            prompt = build_analysis_prompt(platform_name, include_archive=include_archive)

            # Truncate HTML if too long (to stay under token limits)
            max_html_length = 50000  # characters
            if len(html_content) > max_html_length:
                logger.warning(
                    f"HTML content too long ({len(html_content)} chars), "
                    f"truncating to {max_html_length}"
                )
                html_content = html_content[:max_html_length] + "\n... [truncated]"

            # Call Gemini API with vision + text
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=screenshot_bytes, mime_type="image/png"),
                    f"HTML Structure:\n```html\n{html_content}\n```",
                    prompt,
                ],
            )

            # Parse response
            selectors = self._parse_selectors(response.text)

            logger.info(f"Successfully extracted {len(selectors)} selectors")
            return selectors

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise GeminiAPIException(f"Failed to analyze interface: {e}") from e

    def _parse_selectors(self, response_text: str) -> dict[str, str]:
        """
        Parse selector JSON from Gemini response.

        Args:
            response_text: Raw response text from Gemini

        Returns:
            Dictionary of selector_name -> selector_value

        Raises:
            GeminiAPIException: If parsing fails
        """
        try:
            # Try to extract JSON from response
            # Handle markdown code blocks if present
            text = response_text.strip()

            # Remove markdown code blocks if present
            if text.startswith("```"):
                lines = text.split("\n")
                # Find first { and last }
                json_lines = []
                in_json = False
                for line in lines:
                    if "{" in line and not in_json:
                        in_json = True
                    if in_json:
                        json_lines.append(line)
                    if "}" in line and in_json:
                        break
                text = "\n".join(json_lines)

            # Parse JSON
            result = json.loads(text)

            # Check if this is archive format (has "selectors" and "archive_selectors" keys)
            if isinstance(result, dict) and "archive_selectors" in result:
                # Archive format - validate both sections
                selectors = result.get("selectors", {})
                archive_selectors = result.get("archive_selectors", {})

                # Validate required basic selectors
                required_fields = [
                    "input_field",
                    "send_button",
                    "message_bubble_user",
                    "conversation_list",
                    "unread_indicator",
                ]

                for field in required_fields:
                    if field not in selectors:
                        raise ValueError(f"Missing required field in selectors: {field}")
                    if not selectors[field] or selectors[field].strip() == "":
                        raise ValueError(f"Empty selector for field: {field}")

                # message_bubble_bot is optional (can be None/null)
                if "message_bubble_bot" not in selectors:
                    selectors["message_bubble_bot"] = None

                # Validate required archive selectors
                required_archive_fields = [
                    "conversation_item",
                    "profile_name",
                    "profile_picture",
                    "message_container",
                    "scroll_container",
                ]

                for field in required_archive_fields:
                    if field not in archive_selectors:
                        raise ValueError(f"Missing required field in archive_selectors: {field}")
                    if not archive_selectors[field] or archive_selectors[field].strip() == "":
                        raise ValueError(f"Empty archive selector for field: {field}")

                logger.debug(f"Parsed archive format with {len(selectors)} basic and {len(archive_selectors)} archive selectors")
                return result

            else:
                # Old format - just selectors dict
                selectors = result

                # Validate required fields
                required_fields = [
                    "input_field",
                    "send_button",
                    "message_bubble_user",
                    "conversation_list",
                    "unread_indicator",
                ]

                for field in required_fields:
                    if field not in selectors:
                        raise ValueError(f"Missing required field: {field}")
                    if not selectors[field] or selectors[field].strip() == "":
                        raise ValueError(f"Empty selector for field: {field}")

                # message_bubble_bot is optional (can be None/null)
                if "message_bubble_bot" not in selectors:
                    selectors["message_bubble_bot"] = None

                logger.debug(f"Parsed selectors: {selectors}")
                return selectors

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse selector JSON: {e}")
            logger.error(f"Raw response: {response_text}")
            raise GeminiAPIException(f"Invalid selector JSON from Gemini: {e}") from e

    def test_connection(self) -> bool:
        """
        Test Gemini API connection.

        Returns:
            True if connection successful

        Raises:
            GeminiAPIException: If connection fails
        """
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=["Hello, can you respond with 'OK'?"]
            )
            logger.info("Gemini API connection successful")
            return "OK" in response.text or "ok" in response.text.lower()
        except Exception as e:
            logger.error(f"Gemini API connection failed: {e}")
            raise GeminiAPIException(f"Failed to connect to Gemini API: {e}") from e
