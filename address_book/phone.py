import re

from common import Field


class Phone(Field):
    """Contact phone number, stored as '+<country code><number>'.

    The input may contain spaces, hyphens, dots and parentheses. A national
    number (0501234567) or a 380-prefixed one gets the '+380' code, a number
    with a leading '+' keeps its own country code.
    """

    COUNTRY_CODE = "38"
    NATIONAL_LENGTH = 10
    MIN_DIGITS = 10
    MAX_DIGITS = 15

    def __init__(self, value: str):
        normalized = Phone.normalize(value)
        if normalized is None:
            raise ValueError("Invalid phone number. Use 0501234567 or +<country code><number>.")
        super().__init__(normalized)

    @staticmethod
    def normalize(phone_number: str) -> str | None:
        """Return the number in the '+<digits>' format, or None if it is invalid."""
        if not isinstance(phone_number, str):
            return None
        text = phone_number.strip()
        has_plus = text.startswith("+")
        body = text[1:] if has_plus else text
        if re.fullmatch(r"[0-9\s\-().]+", body) is None:
            return None
        digits = re.sub(r"\D", "", body)
        if has_plus:
            return f"+{digits}" if Phone.MIN_DIGITS <= len(digits) <= Phone.MAX_DIGITS else None
        if len(digits) == Phone.NATIONAL_LENGTH and digits.startswith("0"):
            return f"+{Phone.COUNTRY_CODE}{digits}"
        if len(digits) == Phone.NATIONAL_LENGTH + len(Phone.COUNTRY_CODE) and digits.startswith(Phone.COUNTRY_CODE + "0"):
            return f"+{digits}"
        return None

    @staticmethod
    def to_key(phone_number: str) -> str:
        """Return the key used to compare phone numbers.

        It is the normalized number, or the stripped raw value if it cannot be normalized.
        """
        normalized = Phone.normalize(phone_number)
        return phone_number.strip() if normalized is None else normalized

    @property
    def key(self) -> str:
        """Key identifying this phone within a record."""
        return self.value

    @property
    def national_digits(self) -> str:
        """Digits of the number in the national form, e.g. 0501234567 for +380501234567."""
        digits = self.value[1:]
        if len(digits) == Phone.NATIONAL_LENGTH + len(Phone.COUNTRY_CODE) and digits.startswith(Phone.COUNTRY_CODE + "0"):
            return digits[len(Phone.COUNTRY_CODE):]
        return digits
