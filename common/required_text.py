from .field import Field


class RequiredText(Field):
    """Text field that must not be empty.

    Subclasses set `ERROR_MESSAGE` and may override `normalize` to change how
    the stored value is cleaned up.
    """

    ERROR_MESSAGE = "Value cannot be empty."

    def __init__(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(self.ERROR_MESSAGE)
        super().__init__(self.normalize(value))

    @staticmethod
    def normalize(value: str) -> str:
        """Return the value as it is stored, with surrounding whitespace removed."""
        return value.strip()
