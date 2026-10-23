import unittest
from datetime import date
from unittest.mock import patch

from address_book import AddressBook, Record


def make_fake_date(today: date):
    """Return a date subclass whose today() is fixed."""

    class FakeDate(date):
        @classmethod
        def today(cls):
            return cls(today.year, today.month, today.day)

    return FakeDate


class AddressBookTest(unittest.TestCase):
    def test_find_is_case_insensitive(self):
        book = AddressBook()
        record = Record("Alice")
        self.assertTrue(book.add_record(record))
        self.assertFalse(book.add_record(Record("alice")))
        self.assertIs(book.find("ALICE"), record)
        self.assertTrue(book.delete("alice"))
        self.assertIsNone(book.find("Alice"))


class UpcomingBirthdaysTest(unittest.TestCase):
    def upcoming(self, today: date, birthdays: dict[str, str]) -> dict[str, date]:
        book = AddressBook()
        for name, birthday in birthdays.items():
            record = Record(name)
            if birthday:
                record.add_birthday(birthday)
            book.add_record(record)
        with patch("address_book.address_book.date", make_fake_date(today)):
            result = book.get_upcoming_birthdays()
        return {item.record.name.value: item.congratulation_date for item in result}

    def test_window_boundaries(self):
        # 2026-10-23 is a Friday
        result = self.upcoming(date(2026, 10, 23), {
            "Today": "23.10.1990",
            "Day6": "29.10.1985",
            "Day7": "30.10.1985",
            "Yesterday": "22.10.1992",
            "NoBirthday": "",
        })
        self.assertEqual(result, {"Today": date(2026, 10, 23), "Day6": date(2026, 10, 29)})

    def test_weekend_moves_to_monday(self):
        # Saturday and Sunday both move to Monday 2026-10-26
        result = self.upcoming(date(2026, 10, 23), {
            "Saturday": "24.10.1990",
            "Sunday": "25.10.1990",
        })
        self.assertEqual(result, {"Saturday": date(2026, 10, 26), "Sunday": date(2026, 10, 26)})

    def test_custom_window(self):
        book = AddressBook()
        for name, birthday in {"Day2": "25.10.1990", "Day3": "26.10.1990"}.items():
            record = Record(name)
            record.add_birthday(birthday)
            book.add_record(record)
        with patch("address_book.address_book.date", make_fake_date(date(2026, 10, 23))):
            result = book.get_upcoming_birthdays(upcoming_days=3)
        self.assertEqual([item.record.name.value for item in result], ["Day2"])

    def test_year_boundary(self):
        result = self.upcoming(date(2026, 12, 29), {"NewYear": "01.01.1990"})
        self.assertEqual(result, {"NewYear": date(2027, 1, 1)})

    def test_feb_29_in_non_leap_year(self):
        # 2026-03-01 is a Sunday, so the congratulation moves to Monday 2026-03-02
        result = self.upcoming(date(2026, 2, 25), {"Leap": "29.02.2000"})
        self.assertEqual(result, {"Leap": date(2026, 3, 2)})


if __name__ == "__main__":
    unittest.main()
