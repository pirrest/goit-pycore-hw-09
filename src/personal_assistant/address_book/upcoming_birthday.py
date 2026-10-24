import datetime as dt
from dataclasses import dataclass

from .record import Record


@dataclass
class UpcomingBirthday:
    """A record whose birthday is coming up.

    `congratulation_date` is the date to congratulate on, `birthday_date` is
    the actual birthday, which differs when the birthday falls on a weekend.
    """

    record: Record
    congratulation_date: dt.date
    birthday_date: dt.date
