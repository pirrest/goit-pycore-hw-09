import datetime as dt
import unittest

from address_book import Birthday, Name, Phone


class BirthdayTest(unittest.TestCase):
    def test_parses_valid_date(self):
        birthday = Birthday("05.03.1990")
        self.assertEqual(birthday.value, dt.date(1990, 3, 5))
        self.assertEqual(str(birthday), "05.03.1990")

    def test_rejects_invalid_values(self):
        for value in ["1990-03-05", "31.02.2000", "5.3.1990", "05.03.90", "abc", "", "05.03", None]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Use DD.MM.YYYY"):
                    Birthday(value)

    def test_future_date_is_allowed(self):
        self.assertEqual(Birthday("01.01.2999").value, dt.date(2999, 1, 1))


class PhoneTest(unittest.TestCase):
    def test_accepts_ten_digits(self):
        self.assertEqual(Phone("0501234567").value, "0501234567")

    def test_rejects_invalid_values(self):
        for value in ["050123456", "05012345678", "05012345ab", "+380501234567", "", None]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Phone(value)


class NameTest(unittest.TestCase):
    def test_rejects_empty_name(self):
        for value in ["", "   ", None]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Name(value)

    def test_key_is_case_insensitive(self):
        self.assertEqual(Name(" Alice ").key, Name("ALICE").key)


if __name__ == "__main__":
    unittest.main()
