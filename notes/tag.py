from common import Field


class Tag(Field):
    """Note tag, a single lowercase word entered with or without a leading '#'."""

    def __init__(self, value: str):
        tag = value.strip().lstrip("#").casefold() if isinstance(value, str) else ""
        if not tag or any(char.isspace() or char == "#" for char in tag):
            raise ValueError("Tag must be a single word without spaces.")
        super().__init__(tag)

    def __str__(self) -> str:
        return f"#{self.value}"

    @staticmethod
    def to_key(tag: str) -> str:
        """Return the key used to compare tags."""
        return tag.strip().lstrip("#").casefold()

    @property
    def key(self) -> str:
        """Key identifying this tag within a note."""
        return self.value
