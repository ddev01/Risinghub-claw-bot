class ClawError(Exception):
    """Base error for claw bot failures."""


class AlreadyRanError(ClawError):
    """Raised when the claw has already run for the current period."""


class LoginError(ClawError):
    """Raised when login fails or credentials are rejected."""


class BrowserError(ClawError):
    """Raised when browser automation fails."""
