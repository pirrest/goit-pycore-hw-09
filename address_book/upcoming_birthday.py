import datetime as dt
from dataclasses import dataclass

from .record import Record


@dataclass
class UpcomingBirthday:
    """A record whose birthday is coming up, with the date to congratulate on."""

    record: Record
    congratulation_date: dt.date
