class MessagingError(Exception):
    """Base exception for all messaging errors."""
    pass

class AuthenticationError(MessagingError):
    """Raised when authentication fails."""
    pass

class ValidationError(MessagingError):
    """Raised when input validation fails."""
    pass

class NotFoundError(MessagingError):
    """Raised when a resource is not found."""
    pass

class ServerError(MessagingError):
    """Raised when the server returns an error."""
    pass
