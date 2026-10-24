import re

from .address import Address
from .birthday import Birthday
from .email import Email
from .name import Name
from .phone import Phone


class Record:
    """Contact record with a name, phones, emails, addresses and an optional birthday."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.emails: list[Email] = []
        self.addresses: list[Address] = []
        self.birthday: Birthday | None = None

    def __str__(self) -> str:
        birthday = "-" if self.birthday is None else self.birthday
        return (
            f"Contact name: {self.name.value}, "
            f"phones: {'; '.join(p.value for p in self.phones)}, "
            f"emails: {'; '.join(e.value for e in self.emails)}, "
            f"addresses: {'; '.join(a.value for a in self.addresses)}, "
            f"birthday: {birthday}"
        )

    @staticmethod
    def _index_of(items: list, key: str) -> int | None:
        """Return the index of the item with the given key, or None."""
        for index, item in enumerate(items):
            if item.key == key:
                return index
        return None

    @staticmethod
    def _add(items: list, new_item) -> bool:
        """Append the item unless one with the same key is present."""
        if Record._index_of(items, new_item.key) is not None:
            return False
        items.append(new_item)
        return True

    @staticmethod
    def _remove(items: list, key: str) -> bool:
        """Remove the item with the given key."""
        index = Record._index_of(items, key)
        if index is None:
            return False
        del items[index]
        return True

    @staticmethod
    def _edit(items: list, old_key: str, new_item) -> bool:
        """Replace the item with the given key in place.

        Returns:
            False if the old item was not found or the new one equals another item.
        """
        index = Record._index_of(items, old_key)
        if index is None:
            return False
        other_index = Record._index_of(items, new_item.key)
        if other_index is not None and other_index != index:
            return False
        items[index] = new_item
        return True

    def edit_name(self, new_name: str) -> None:
        """Rename the contact.

        Raises:
            ValueError: If the new name is empty.
        """
        self.name = Name(new_name)

    def add_phone(self, phone_number: str) -> bool:
        """Add a phone to the record.

        Returns:
            True if added, False if the record already has this phone.

        Raises:
            ValueError: If the number is invalid.
        """
        return Record._add(self.phones, Phone(phone_number))

    def remove_phone(self, phone_number: str) -> bool:
        """Remove a phone from the record.

        Returns:
            True if removed, False if the phone was not found.
        """
        return Record._remove(self.phones, Phone.to_key(phone_number))

    def edit_phone(self, old_phone_number: str, new_phone_number: str) -> bool:
        """Replace a phone in place, keeping its position in the list.

        Returns:
            True if replaced, False if the old phone was not found or the new
            number is already present in the record as another phone.

        Raises:
            ValueError: If the new number is invalid.
        """
        return Record._edit(self.phones, Phone.to_key(old_phone_number), Phone(new_phone_number))

    def find_phone(self, phone_number: str) -> Phone | None:
        """Return the phone matching the given number, or None if not found."""
        index = Record._index_of(self.phones, Phone.to_key(phone_number))
        return None if index is None else self.phones[index]

    def add_email(self, email: str) -> bool:
        """Add an email to the record.

        Returns:
            True if added, False if the record already has this email.

        Raises:
            ValueError: If the email is invalid.
        """
        return Record._add(self.emails, Email(email))

    def remove_email(self, email: str) -> bool:
        """Remove an email from the record.

        Returns:
            True if removed, False if the email was not found.
        """
        return Record._remove(self.emails, Email.to_key(email))

    def edit_email(self, old_email: str, new_email: str) -> bool:
        """Replace an email in place, keeping its position in the list.

        Returns:
            True if replaced, False if the old email was not found or the new
            one is already present in the record as another email.

        Raises:
            ValueError: If the new email is invalid.
        """
        return Record._edit(self.emails, Email.to_key(old_email), Email(new_email))

    def find_email(self, email: str) -> Email | None:
        """Return the email matching the given one, or None if not found."""
        index = Record._index_of(self.emails, Email.to_key(email))
        return None if index is None else self.emails[index]

    def add_address(self, address: str) -> bool:
        """Add an address to the record.

        Returns:
            True if added, False if the record already has this address.

        Raises:
            ValueError: If the address is empty.
        """
        return Record._add(self.addresses, Address(address))

    def remove_address(self, address: str) -> bool:
        """Remove an address from the record.

        Returns:
            True if removed, False if the address was not found.
        """
        return Record._remove(self.addresses, Address.to_key(address))

    def edit_address(self, old_address: str, new_address: str) -> bool:
        """Replace an address in place, keeping its position in the list.

        Returns:
            True if replaced, False if the old address was not found or the new
            one is already present in the record as another address.

        Raises:
            ValueError: If the new address is empty.
        """
        return Record._edit(self.addresses, Address.to_key(old_address), Address(new_address))

    def find_address(self, address: str) -> Address | None:
        """Return the address matching the given one, or None if not found."""
        index = Record._index_of(self.addresses, Address.to_key(address))
        return None if index is None else self.addresses[index]

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

    def matches(self, text: str) -> bool:
        """Check whether the text occurs in any field of the record, ignoring case.

        A text made only of phone characters is also compared by digits with
        the phones, both in the international and the national form.
        """
        needle = text.strip().casefold()
        if not needle:
            return False
        values = [self.name.value, *(e.value for e in self.emails), *(a.value for a in self.addresses)]
        if self.birthday is not None:
            values.append(str(self.birthday))
        values.extend(p.value for p in self.phones)
        if any(needle in value.casefold() for value in values):
            return True
        if re.fullmatch(r"[0-9\s\-+().]+", needle):
            digits = re.sub(r"\D", "", needle)
            return bool(digits) and any(
                digits in p.value or digits in p.national_digits for p in self.phones
            )
        return False
