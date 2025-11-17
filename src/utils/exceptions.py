"""Custom exceptions for the chatoperator system."""


class ChatOperatorException(Exception):
    """Base exception for all chatoperator errors."""

    pass


class SelectorNotFoundException(ChatOperatorException):
    """Raised when a selector cannot find an element on the page."""

    pass


class AuthenticationFailedException(ChatOperatorException):
    """Raised when authentication to a platform fails."""

    pass


class PlatformNotConfiguredException(ChatOperatorException):
    """Raised when trying to operate on a platform without cached configuration."""

    pass


class RecalibrationRequiredException(ChatOperatorException):
    """Raised when selectors fail and recalibration is needed."""

    pass


class GeminiAPIException(ChatOperatorException):
    """Raised when Gemini API calls fail."""

    pass


class ChatbotAPIException(ChatOperatorException):
    """Raised when chatbot API calls fail."""

    pass
