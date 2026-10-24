from personal_assistant.common import RequiredText


class Name(RequiredText):
    """Required contact name, must not be empty."""

    ERROR_MESSAGE = "Name cannot be empty."

    @staticmethod
    def to_key(name: str) -> str:
        """Return the case- and surrounding-whitespace-insensitive key for a name."""
        return name.strip().casefold()

    @property
    def key(self) -> str:
        """Key identifying this name in an address book."""
        return Name.to_key(self.value)
