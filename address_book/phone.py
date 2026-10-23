import re

from .field import Field


class Phone(Field):
    """Contact phone number, must consist of exactly 10 ASCII digits."""

    COUNTRY_CODE = "+38"

    def __init__(self, value: str):
        if not isinstance(value, str) or re.fullmatch(r"[0-9]{10}", value) is None:
            raise ValueError("Phone number must consist of 10 digits.")
        super().__init__(value)

    @staticmethod
    def normalize_phone(phone_number: str) -> str | None:
        """Normalize a phone number to the '+<digits>' format.

        All characters except digits and a leading '+' are removed. A number that
        already has a '+' keeps its country code, one starting with '380' gets only
        the '+', any other number gets the default '+38' prefix.

        Args:
            phone_number: Phone number in an arbitrary format.

        Returns:
            Normalized number, or None if the input is not a string or has no digits.
        """
        if not isinstance(phone_number, str):
            return None
        digits = re.sub(r"\D", "", phone_number)
        if not digits:
            return None
        if re.match(r"\s*\+", phone_number):
            return f"+{digits}"
        if digits.startswith(Phone.COUNTRY_CODE.lstrip("+") + "0"):
            return f"+{digits}"
        return f"{Phone.COUNTRY_CODE}{digits}"

    @staticmethod
    def to_key(phone_number: str) -> str:
        """Return the key used to compare phone numbers.

        It is the normalized number, or the raw value if it cannot be normalized.
        """
        normalized = Phone.normalize_phone(phone_number)
        return phone_number if normalized is None else normalized

    @property
    def key(self) -> str:
        """Key identifying this phone within a record."""
        return Phone.to_key(self.value)
