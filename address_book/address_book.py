from collections import UserDict
from datetime import date

from .address_book_storage import AddressBookStorage
from .name import Name
from .record import Record
from .upcoming_birthday import UpcomingBirthday


class AddressBook(UserDict):
    """Collection of records keyed by the case-insensitive contact name."""

    def save(self, filename: str = AddressBookStorage.DEFAULT_FILENAME) -> None:
        """Write the book to a file."""
        AddressBookStorage(filename).save(self)

    @classmethod
    def load(cls, filename: str = AddressBookStorage.DEFAULT_FILENAME) -> "AddressBook":
        """Return the book stored in a file, or an empty one if it is missing or corrupted."""
        book = AddressBookStorage(filename).load()
        return cls() if book is None else book

    def add_record(self, record: Record) -> bool:
        """Add a record to the book.

        Returns:
            True if added, False if a record with the same name already exists.
        """
        key = record.key
        if key in self.data:
            return False
        self.data[key] = record
        return True

    def find(self, name: str) -> Record | None:
        """Return the record with the given name, or None if not found."""
        return self.data.get(Name.to_key(name))

    def delete(self, name: str) -> bool:
        """Delete the record with the given name.

        Returns:
            True if deleted, False if the record was not found.
        """
        key = Name.to_key(name)
        if key not in self.data:
            return False
        del self.data[key]
        return True

    def get_upcoming_birthdays(self, upcoming_days: int | None = None) -> list[UpcomingBirthday]:
        """Return records whose birthday falls within the next days, including today.

        A congratulation date that falls on a weekend is moved to the next Monday.
        Records without a birthday are skipped.

        Args:
            upcoming_days: Window size in days, `Birthday.UPCOMING_DAYS` by default.
        """
        today = date.today()
        result = []
        for record in self.data.values():
            if record.birthday is None:
                continue
            congratulation_date = record.birthday.upcoming_congratulation_date(today, upcoming_days)
            if congratulation_date is not None:
                result.append(UpcomingBirthday(record, congratulation_date))
        return result
