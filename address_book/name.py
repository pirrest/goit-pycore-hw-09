from .field import Field


class Name(Field):
    """Required contact name, must not be empty."""

    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

    @staticmethod
    def to_key(name: str) -> str:
        """Return the case- and surrounding-whitespace-insensitive key for a name."""
        return name.strip().casefold()

    @property
    def key(self) -> str:
        """Key identifying this name in an address book."""
        return Name.to_key(self.value)
