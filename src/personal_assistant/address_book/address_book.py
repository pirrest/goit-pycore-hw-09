from collections import UserList
from datetime import date

from personal_assistant.storage import FileStorage

from .name import Name
from .record import Record
from .upcoming_birthday import UpcomingBirthday


class AddressBook(UserList):
    """List of contact records; several records may share a name."""

    DEFAULT_FILENAME = "contacts.pkl"

    def save(self, filename: str | None = None) -> None:
        """Write the book to a file, `contacts.pkl` in the assistant folder by default."""
        FileStorage(filename or FileStorage.default_path(self.DEFAULT_FILENAME)).save(self)

    @classmethod
    def load(cls, filename: str | None = None) -> "AddressBook":
        """Return the book stored in a file, or an empty one if it is missing or corrupted."""
        book = FileStorage(filename or FileStorage.default_path(cls.DEFAULT_FILENAME)).load()
        return cls() if book is None else book

    def add_record(self, record: Record) -> None:
        """Append a record to the book."""
        self.data.append(record)

    def find_by_name(self, name: str, exact: bool = False) -> list[Record]:
        """Return the records whose name matches, ignoring case.

        Args:
            name: Full name, or a part of it when `exact` is False.
            exact: Require the whole name to match instead of a part of it.
        """
        key = Name.to_key(name)
        if exact:
            return [record for record in self.data if record.name.key == key]
        return [record for record in self.data if key in record.name.key]

    def search(self, text: str) -> list[Record]:
        """Return the records that contain the text in any field, ignoring case."""
        return [record for record in self.data if record.matches(text)]

    def delete(self, record: Record) -> bool:
        """Delete the given record from the book.

        Returns:
            True if deleted, False if the record is not in the book.
        """
        for index, item in enumerate(self.data):
            if item is record:
                del self.data[index]
                return True
        return False

    def get_upcoming_birthdays(self, upcoming_days: int | None = None) -> list[UpcomingBirthday]:
        """Return records whose birthday falls within the next days, including today.

        A congratulation date that falls on a weekend is moved to the next Monday.
        Records without a birthday are skipped.

        Args:
            upcoming_days: Window size in days, `Birthday.UPCOMING_DAYS` by default.
        """
        today = date.today()
        result = []
        for record in self.data:
            if record.birthday is None:
                continue
            congratulation_date = record.birthday.upcoming_congratulation_date(today, upcoming_days)
            if congratulation_date is not None:
                result.append(
                    UpcomingBirthday(record, congratulation_date, record.birthday.next_birthday(today))
                )
        return result
