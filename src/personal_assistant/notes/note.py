import datetime as dt

from .tag import Tag
from .text import Text
from .title import Title


class Note:
    """Text note with a title, tags and the creation time."""

    DATE_FORMAT = "%d.%m.%Y %H:%M"

    def __init__(self, title: str, text: str, tags: list[str] | None = None):
        self.title = Title(title)
        self.text = Text(text)
        self.tags: list[Tag] = []
        for tag in tags or []:
            self.add_tag(tag)
        self.created_at = dt.datetime.now()

    def __str__(self) -> str:
        tags = f" [{' '.join(str(tag) for tag in self.tags)}]" if self.tags else ""
        return f"{self.title}: {self.text}{tags} ({self.created_at:{Note.DATE_FORMAT}})"

    def edit_title(self, title: str) -> None:
        """Replace the title.

        Raises:
            ValueError: If the title is empty.
        """
        self.title = Title(title)

    def edit_text(self, text: str) -> None:
        """Replace the text.

        Raises:
            ValueError: If the text is empty.
        """
        self.text = Text(text)

    def add_tag(self, tag: str) -> bool:
        """Add a tag to the note.

        Returns:
            True if added, False if the note already has this tag.

        Raises:
            ValueError: If the tag is not a single word.
        """
        new_tag = Tag(tag)
        if self.has_tag(new_tag.value):
            return False
        self.tags.append(new_tag)
        return True

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the note.

        Returns:
            True if removed, False if the note does not have this tag.
        """
        key = Tag.to_key(tag)
        for index, existing in enumerate(self.tags):
            if existing.key == key:
                del self.tags[index]
                return True
        return False

    def has_tag(self, tag: str) -> bool:
        """Check whether the note has the tag."""
        key = Tag.to_key(tag)
        return any(existing.key == key for existing in self.tags)

    def matches(self, text: str) -> bool:
        """Check whether the text occurs in the title or the text of the note, ignoring case."""
        needle = text.strip().casefold()
        return bool(needle) and (
            needle in self.title.value.casefold() or needle in self.text.value.casefold()
        )
