import datetime as dt
import re

from common import Field


class Birthday(Field):
    """Contact birthday, stored as a date and entered as DD.MM.YYYY."""

    FORMAT = "%d.%m.%Y"
    WEEKEND_DAYS = (5, 6)
    UPCOMING_DAYS = 7

    def __init__(self, value: str):
        try:
            # strptime alone accepts days and months without a leading zero
            if re.fullmatch(r"[0-9]{2}\.[0-9]{2}\.[0-9]{4}", value) is None:
                raise ValueError
            birth_date = dt.datetime.strptime(value, Birthday.FORMAT).date()
        except (ValueError, TypeError):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(birth_date)

    def __str__(self) -> str:
        return self.value.strftime(Birthday.FORMAT)

    def _in_year(self, year: int) -> dt.date:
        """Return the birthday in the given year, moving Feb 29 to Mar 1 in non-leap years."""
        try:
            return self.value.replace(year=year)
        except ValueError:
            return dt.date(year, 3, 1)

    def next_birthday(self, today: dt.date) -> dt.date:
        """Return the nearest birthday that is today or later."""
        next_birthday = self._in_year(today.year)
        if next_birthday < today:
            # Already passed this year, so the next one is in the following year
            next_birthday = self._in_year(today.year + 1)
        return next_birthday

    def upcoming_congratulation_date(
        self, today: dt.date, upcoming_days: int | None = None
    ) -> dt.date | None:
        """Return the date to congratulate on, or None if the birthday is not upcoming.

        The window of `upcoming_days` days includes today. A congratulation date
        that falls on a weekend is moved to the next Monday.

        Args:
            today: The date to count from.
            upcoming_days: Window size in days, `Birthday.UPCOMING_DAYS` by default.
        """
        if upcoming_days is None:
            upcoming_days = Birthday.UPCOMING_DAYS
        next_birthday = self.next_birthday(today)
        if (next_birthday - today).days >= upcoming_days:
            return None
        if next_birthday.weekday() in Birthday.WEEKEND_DAYS:
            # Shift the congratulation to the next Monday
            next_birthday += dt.timedelta(days=7 - next_birthday.weekday())
        return next_birthday
