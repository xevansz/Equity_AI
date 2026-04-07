"""Custom exception classes for consistent error handling"""

from typing import Any


class EquityAIException(Exception):
    """Base exception for all Equity AI errors"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(EquityAIException):
    """Database connection or operation errors"""

    pass


class AuthenticationError(EquityAIException):
    """Authentication and authorization errors"""

    pass


class ValidationError(EquityAIException):
    """Data validation errors"""

    pass


class ExternalAPIError(EquityAIException):
    """External API call failures"""

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.provider = provider
        self.status_code = status_code
        super().__init__(message, details)


class RateLimitError(ExternalAPIError):
    """API rate limit exceeded"""

    pass


class DataNotFoundError(EquityAIException):
    """Requested data not found"""

    pass


class VectorStoreError(EquityAIException):
    """Vector store operation errors"""

    pass


class LLMError(EquityAIException):
    """LLM service errors"""

    pass


class ConfigurationError(EquityAIException):
    """Configuration or environment errors"""

    pass
