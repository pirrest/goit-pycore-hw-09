from .birthday import Birthday
from .name import Name
from .phone import Phone


class Record:
    """Contact record with a name, a list of phones and an optional birthday."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None

    @property
    def key(self) -> str:
        """Key identifying this record in an address book."""
        return self.name.key

    def __str__(self) -> str:
        birthday = "-" if self.birthday is None else self.birthday
        return (
            f"Contact name: {self.name.value}, "
            f"phones: {'; '.join(p.value for p in self.phones)}, "
            f"birthday: {birthday}"
        )

    def _index_of_phone(self, phone_number: str) -> int | None:
        """Return the index of the phone matching the given number, or None."""
        key = Phone.to_key(phone_number)
        for index, phone in enumerate(self.phones):
            if phone.key == key:
                return index
        return None

    def add_phone(self, phone_number: str) -> bool:
        """Add a phone to the record.

        Returns:
            True if added, False if the record already has this phone.

        Raises:
            ValueError: If the number is not 10 digits.
        """
        phone = Phone(phone_number)
        if self._index_of_phone(phone_number) is not None:
            return False
        self.phones.append(phone)
        return True

    def remove_phone(self, phone_number: str) -> bool:
        """Remove a phone from the record.

        Returns:
            True if removed, False if the phone was not found.
        """
        index = self._index_of_phone(phone_number)
        if index is None:
            return False
        del self.phones[index]
        return True

    def edit_phone(self, old_phone_number: str, new_phone_number: str) -> bool:
        """Replace a phone in place, keeping its position in the list.

        Returns:
            True if replaced, False if the old phone was not found or the new
            number is already present in the record as another phone.

        Raises:
            ValueError: If the new number is not 10 digits.
        """
        new_phone = Phone(new_phone_number)
        index = self._index_of_phone(old_phone_number)
        if index is None:
            return False
        for other_index, phone in enumerate(self.phones):
            if other_index != index and phone.key == new_phone.key:
                return False
        self.phones[index] = new_phone
        return True

    def find_phone(self, phone_number: str) -> Phone | None:
        """Return the phone matching the given number, or None if not found."""
        index = self._index_of_phone(phone_number)
        return None if index is None else self.phones[index]

    def add_birthday(self, birthday: str) -> bool:
        """Set the birthday, replacing the previous one if any.

        Args:
            birthday: Date string in the DD.MM.YYYY format.

        Returns:
            True if a birthday was already set and got replaced, False otherwise.

        Raises:
            ValueError: If the date format is invalid.
        """
        new_birthday = Birthday(birthday)
        replaced = self.birthday is not None
        self.birthday = new_birthday
        return replaced
