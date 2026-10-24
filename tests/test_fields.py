import datetime as dt
import unittest

from personal_assistant.address_book import Address, Birthday, Email, Name, Phone


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
    def test_normalizes_to_one_format(self):
        for value in [
            "0501234567",
            "050-123-45-67",
            "(050) 123 45 67",
            "050.123.45.67",
            "380501234567",
            "+380501234567",
            "+38 (050) 123-45-67",
            "  0501234567  ",
        ]:
            with self.subTest(value=value):
                self.assertEqual(Phone(value).value, "+380501234567")

    def test_keeps_foreign_country_code(self):
        self.assertEqual(Phone("+48 600 700 800").value, "+48600700800")
        self.assertEqual(Phone("+1 (202) 555-0143").value, "+12025550143")

    def test_rejects_invalid_values(self):
        for value in [
            "050123456",
            "05012345678",
            "1234567890",
            "05012345ab",
            "+123456789",
            "+1234567890123456",
            "",
            "+",
            None,
        ]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Invalid phone number"):
                    Phone(value)

    def test_to_key(self):
        self.assertEqual(Phone.to_key("050 123 45 67"), "+380501234567")
        self.assertEqual(Phone.to_key(" garbage "), "garbage")

    def test_national_digits(self):
        self.assertEqual(Phone("0501234567").national_digits, "0501234567")
        self.assertEqual(Phone("+48600700800").national_digits, "48600700800")


class EmailTest(unittest.TestCase):
    def test_accepts_valid_emails(self):
        for value in ["a@b.com", "john.doe+tag@mail.example.org", "  a@b.co  "]:
            with self.subTest(value=value):
                self.assertEqual(Email(value).value, value.strip())

    def test_rejects_invalid_emails(self):
        for value in ["", "abc", "a@b", "a@.com", "a b@c.com", "a@@b.com", "@b.com", "a@b..com", None]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Invalid email"):
                    Email(value)

    def test_key_is_case_insensitive(self):
        self.assertEqual(Email("A@B.com").key, Email("a@b.COM").key)


class AddressTest(unittest.TestCase):
    def test_rejects_empty_address(self):
        for value in ["", "   ", None]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Address(value)

    def test_collapses_whitespace_and_compares_ignoring_case(self):
        self.assertEqual(Address("  Kyiv,   Main st 1 ").value, "Kyiv, Main st 1")
        self.assertEqual(Address("KYIV, main st 1").key, Address("Kyiv,  Main st 1").key)


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
