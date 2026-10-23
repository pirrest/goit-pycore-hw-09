import datetime as dt
import unittest

from address_book import Record


class RecordTest(unittest.TestCase):
    def setUp(self):
        self.record = Record("Alice")

    def test_add_phone_validates_and_rejects_duplicates(self):
        self.assertTrue(self.record.add_phone("0501234567"))
        self.assertFalse(self.record.add_phone("0501234567"))
        with self.assertRaises(ValueError):
            self.record.add_phone("123")
        self.assertEqual([p.value for p in self.record.phones], ["0501234567"])

    def test_edit_phone(self):
        self.record.add_phone("0501234567")
        self.record.add_phone("0507654321")
        self.assertTrue(self.record.edit_phone("0501234567", "0509999999"))
        self.assertEqual([p.value for p in self.record.phones], ["0509999999", "0507654321"])
        self.assertFalse(self.record.edit_phone("0000000000", "0501111111"))
        self.assertFalse(self.record.edit_phone("0509999999", "0507654321"))
        with self.assertRaises(ValueError):
            self.record.edit_phone("0509999999", "bad")

    def test_remove_and_find_phone(self):
        self.record.add_phone("0501234567")
        self.assertIsNotNone(self.record.find_phone("0501234567"))
        self.assertTrue(self.record.remove_phone("0501234567"))
        self.assertFalse(self.record.remove_phone("0501234567"))
        self.assertIsNone(self.record.find_phone("0501234567"))

    def test_add_birthday_replaces_previous(self):
        self.assertFalse(self.record.add_birthday("05.03.1990"))
        self.assertTrue(self.record.add_birthday("06.03.1991"))
        self.assertEqual(self.record.birthday.value, dt.date(1991, 3, 6))

    def test_invalid_birthday_keeps_previous(self):
        self.record.add_birthday("05.03.1990")
        with self.assertRaises(ValueError):
            self.record.add_birthday("nope")
        self.assertEqual(str(self.record.birthday), "05.03.1990")

    def test_str(self):
        self.assertEqual(str(self.record), "Contact name: Alice, phones: , birthday: -")
        self.record.add_phone("0501234567")
        self.record.add_birthday("05.03.1990")
        self.assertEqual(
            str(self.record),
            "Contact name: Alice, phones: 0501234567, birthday: 05.03.1990",
        )


if __name__ == "__main__":
    unittest.main()
