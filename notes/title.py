from common import RequiredText


class Title(RequiredText):
    """Required note title, must not be empty."""

    ERROR_MESSAGE = "Title cannot be empty."

    @staticmethod
    def normalize(value: str) -> str:
        """Return the title with runs of whitespace collapsed to single spaces."""
        return " ".join(value.split())
