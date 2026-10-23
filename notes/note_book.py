from collections import UserList

from storage import FileStorage

from .note import Note


class NoteBook(UserList):
    """List of notes."""

    DEFAULT_FILENAME = "notes.pkl"

    def save(self, filename: str | None = None) -> None:
        """Write the notes to a file, `notes.pkl` in the assistant folder by default."""
        FileStorage(filename or FileStorage.default_path(self.DEFAULT_FILENAME)).save(self)

    @classmethod
    def load(cls, filename: str | None = None) -> "NoteBook":
        """Return the notes stored in a file, or an empty book if it is missing or corrupted."""
        book = FileStorage(filename or FileStorage.default_path(cls.DEFAULT_FILENAME)).load()
        return cls() if book is None else book

    def add_note(self, note: Note) -> None:
        """Append a note to the book."""
        self.data.append(note)

    def search(self, text: str) -> list[Note]:
        """Return the notes that contain the text in the title or the text, ignoring case."""
        return [note for note in self.data if note.matches(text)]

    def find_by_tag(self, tag: str) -> list[Note]:
        """Return the notes that have the tag."""
        return [note for note in self.data if note.has_tag(tag)]

    def group_by_tag(self) -> dict[str, list[Note]]:
        """Group the notes by tag, with the tags in alphabetical order.

        A note with several tags is listed under each of them. Notes without
        tags are not included.
        """
        groups: dict[str, list[Note]] = {}
        for note in self.data:
            for tag in note.tags:
                groups.setdefault(tag.value, []).append(note)
        return dict(sorted(groups.items()))

    def untagged(self) -> list[Note]:
        """Return the notes that have no tags."""
        return [note for note in self.data if not note.tags]

    def delete(self, note: Note) -> bool:
        """Delete the given note from the book.

        Returns:
            True if deleted, False if the note is not in the book.
        """
        for index, item in enumerate(self.data):
            if item is note:
                del self.data[index]
                return True
        return False
