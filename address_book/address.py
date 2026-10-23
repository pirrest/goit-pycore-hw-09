from common import RequiredText


class Address(RequiredText):
    """Contact postal address, must not be empty."""

    ERROR_MESSAGE = "Address cannot be empty."

    @staticmethod
    def normalize(value: str) -> str:
        """Return the address with runs of whitespace collapsed to single spaces."""
        return " ".join(value.split())

    @staticmethod
    def to_key(address: str) -> str:
        """Return the case- and whitespace-insensitive key for an address."""
        return Address.normalize(address).casefold()

    @property
    def key(self) -> str:
        """Key identifying this address within a record."""
        return Address.to_key(self.value)
