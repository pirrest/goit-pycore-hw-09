import re

from common import Field


class Email(Field):
    """Contact email address in the name@domain.tld format."""

    PATTERN = re.compile(r"[^@\s]+@[^@\s.]+(\.[^@\s.]+)+")

    def __init__(self, value: str):
        if not isinstance(value, str) or Email.PATTERN.fullmatch(value.strip()) is None:
            raise ValueError("Invalid email. Use name@domain.com")
        super().__init__(value.strip())

    @staticmethod
    def to_key(email: str) -> str:
        """Return the case- and surrounding-whitespace-insensitive key for an email."""
        return email.strip().casefold()

    @property
    def key(self) -> str:
        """Key identifying this email within a record."""
        return Email.to_key(self.value)
