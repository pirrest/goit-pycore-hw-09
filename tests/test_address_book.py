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
    def test_is_a_list_and_allows_duplicate_names(self):
        book = AddressBook()
        first, second = Record("Alice"), Record("alice")
        book.add_record(first)
        book.add_record(second)
        self.assertEqual(len(book), 2)
        self.assertIs(book[0], first)
        self.assertEqual(list(book), [first, second])

    def test_find_by_name(self):
        book = AddressBook()
        alice, alicia, bob = Record("Alice"), Record("Alicia Smith"), Record("Bob")
        for record in (alice, alicia, bob):
            book.add_record(record)
        self.assertEqual(book.find_by_name("ALICE", exact=True), [alice])
        self.assertEqual(book.find_by_name("ali"), [alice, alicia])
        self.assertEqual(book.find_by_name("smith", exact=True), [])
        self.assertEqual(book.find_by_name("zed"), [])

    def test_search_looks_in_all_fields(self):
        book = AddressBook()
        alice, bob = Record("Alice"), Record("Bob")
        alice.add_email("alice@example.com")
        bob.add_address("Alice Street 5")
        book.add_record(alice)
        book.add_record(bob)
        self.assertEqual(book.search("alice"), [alice, bob])
        self.assertEqual(book.search("example.com"), [alice])
        self.assertEqual(book.search(""), [])

    def test_delete_removes_only_the_given_record(self):
        book = AddressBook()
        first, second = Record("Alice"), Record("Alice")
        book.add_record(first)
        book.add_record(second)
        self.assertTrue(book.delete(second))
        self.assertFalse(book.delete(second))
        self.assertEqual(list(book), [first])


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

    def test_weekend_moves_to_monday_and_keeps_real_birthday(self):
        book = AddressBook()
        record = Record("Saturday")
        record.add_birthday("24.10.1990")
        book.add_record(record)
        with patch("address_book.address_book.date", make_fake_date(date(2026, 10, 23))):
            [item] = book.get_upcoming_birthdays()
        self.assertEqual(item.congratulation_date, date(2026, 10, 26))
        self.assertEqual(item.birthday_date, date(2026, 10, 24))

    def test_sunday_moves_to_monday(self):
        result = self.upcoming(date(2026, 10, 23), {"Sunday": "25.10.1990"})
        self.assertEqual(result, {"Sunday": date(2026, 10, 26)})

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
