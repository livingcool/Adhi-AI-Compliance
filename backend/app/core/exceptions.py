"""
Custom domain exception classes for Adhi Compliance.

These are raised throughout the application and caught by the global exception
handler registered in app/middleware/error_handler.py.
"""


class AdhiBaseException(Exception):
    """Base class for all Adhi Compliance application exceptions."""


class NotFoundError(AdhiBaseException):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id '{entity_id}' not found.")


class UnauthorizedError(AdhiBaseException):
    """Raised when a request lacks valid authentication credentials."""

    def __init__(self, message: str = "Authentication required."):
        self.message = message
        super().__init__(message)


class ForbiddenError(AdhiBaseException):
    """Raised when an authenticated user lacks permission for an action."""

    def __init__(self, message: str = "You do not have permission to perform this action."):
        self.message = message
        super().__init__(message)


class ValidationError(AdhiBaseException):
    """Raised when business-logic validation fails (distinct from Pydantic validation)."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error on '{field}': {message}")


class ConflictError(AdhiBaseException):
    """Raised when an operation would create a conflicting state (e.g. duplicate)."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
