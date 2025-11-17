"""Interface to external chatbot service."""


import requests

from src.config.settings import settings
from src.models.conversation import Conversation
from src.utils.exceptions import ChatbotAPIException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChatbotInterface:
    """Interface to external chatbot API or service."""

    def __init__(
        self, api_url: str | None = None, api_key: str | None = None
    ) -> None:
        """
        Initialize chatbot interface.

        Args:
            api_url: Chatbot API URL (defaults to settings.CHATBOT_API_URL)
            api_key: Chatbot API key (defaults to settings.CHATBOT_API_KEY)
        """
        self.api_url = api_url or settings.CHATBOT_API_URL
        self.api_key = api_key or settings.CHATBOT_API_KEY

        if not self.api_url or not self.api_key:
            logger.warning(
                "Chatbot API not configured. Using echo mode (returns last message)."
            )
            self.echo_mode = True
        else:
            self.echo_mode = False
            logger.info(f"Chatbot API configured: {self.api_url}")

    def get_response(self, conversation: Conversation) -> str:
        """
        Get chatbot response for a conversation.

        Args:
            conversation: Conversation object with message history

        Returns:
            Chatbot response text

        Raises:
            ChatbotAPIException: If API call fails
        """
        # Echo mode (for testing without real chatbot API)
        if self.echo_mode:
            return self._echo_response(conversation)

        # Real chatbot API call
        try:
            # Build request payload
            messages = [
                {"role": msg.sender, "content": msg.text} for msg in conversation.messages
            ]

            payload = {
                "messages": messages,
                "conversation_id": conversation.conversation_id,
                "platform": conversation.platform,
            }

            # Call chatbot API
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30,
            )

            response.raise_for_status()

            result = response.json()
            chatbot_response = result.get("response", "")

            if not chatbot_response:
                raise ChatbotAPIException("Empty response from chatbot API")

            logger.info(f"Got chatbot response ({len(chatbot_response)} chars)")
            return chatbot_response

        except requests.exceptions.RequestException as e:
            logger.error(f"Chatbot API request failed: {e}")
            raise ChatbotAPIException(f"Failed to get chatbot response: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error calling chatbot API: {e}")
            raise ChatbotAPIException(f"Chatbot API error: {e}") from e

    def _echo_response(self, conversation: Conversation) -> str:
        """
        Echo mode: Return a simple response (for testing).

        Args:
            conversation: Conversation object

        Returns:
            Echo response
        """
        if not conversation.messages:
            return "Hello! How can I help you?"

        last_message = conversation.messages[-1]

        # Simple echo response
        response = f"I received your message: '{last_message.text[:50]}...'"

        logger.debug(f"Echo mode response: {response}")
        return response

    def test_connection(self) -> bool:
        """
        Test chatbot API connection.

        Returns:
            True if connection successful or in echo mode
        """
        if self.echo_mode:
            logger.info("Chatbot in echo mode (testing)")
            return True

        try:
            # Simple health check
            response = requests.get(
                self.api_url.replace("/chat", "/health"),
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            response.raise_for_status()
            logger.info("Chatbot API connection successful")
            return True
        except Exception as e:
            logger.error(f"Chatbot API connection failed: {e}")
            return False
