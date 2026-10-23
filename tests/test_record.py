import datetime as dt
import unittest

from address_book import Record


class RecordTest(unittest.TestCase):
    def setUp(self):
        self.record = Record("Alice")

    def test_add_phone_validates_and_rejects_duplicates(self):
        self.assertTrue(self.record.add_phone("0501234567"))
        self.assertFalse(self.record.add_phone("050-123-45-67"))
        with self.assertRaises(ValueError):
            self.record.add_phone("123")
        self.assertEqual([p.value for p in self.record.phones], ["+380501234567"])

    def test_edit_phone(self):
        self.record.add_phone("0501234567")
        self.record.add_phone("0507654321")
        self.assertTrue(self.record.edit_phone("0501234567", "0509999999"))
        self.assertEqual(
            [p.value for p in self.record.phones], ["+380509999999", "+380507654321"]
        )
        self.assertFalse(self.record.edit_phone("0000000000", "0501111111"))
        self.assertFalse(self.record.edit_phone("0509999999", "0507654321"))
        with self.assertRaises(ValueError):
            self.record.edit_phone("0509999999", "bad")

    def test_remove_and_find_phone(self):
        self.record.add_phone("0501234567")
        self.assertIsNotNone(self.record.find_phone("050 123 45 67"))
        self.assertTrue(self.record.remove_phone("0501234567"))
        self.assertFalse(self.record.remove_phone("0501234567"))
        self.assertIsNone(self.record.find_phone("0501234567"))

    def test_emails(self):
        self.assertTrue(self.record.add_email("a@b.com"))
        self.assertFalse(self.record.add_email("A@B.com"))
        self.assertTrue(self.record.add_email("c@d.com"))
        with self.assertRaises(ValueError):
            self.record.add_email("nope")
        self.assertTrue(self.record.edit_email("A@b.com", "x@y.com"))
        self.assertFalse(self.record.edit_email("x@y.com", "c@d.com"))
        self.assertFalse(self.record.edit_email("missing@b.com", "q@w.com"))
        self.assertEqual([e.value for e in self.record.emails], ["x@y.com", "c@d.com"])
        self.assertIsNotNone(self.record.find_email("C@D.com"))
        self.assertTrue(self.record.remove_email("c@d.com"))
        self.assertFalse(self.record.remove_email("c@d.com"))

    def test_addresses(self):
        self.assertTrue(self.record.add_address("Kyiv, Main st 1"))
        self.assertFalse(self.record.add_address("kyiv,  main st 1"))
        self.assertTrue(self.record.add_address("Lviv"))
        self.assertTrue(self.record.edit_address("Lviv", "Odesa"))
        self.assertFalse(self.record.edit_address("Odesa", "Kyiv, Main st 1"))
        self.assertEqual([a.value for a in self.record.addresses], ["Kyiv, Main st 1", "Odesa"])
        self.assertIsNotNone(self.record.find_address("odesa"))
        self.assertTrue(self.record.remove_address("ODESA"))
        with self.assertRaises(ValueError):
            self.record.add_address("  ")

    def test_edit_name(self):
        self.record.edit_name("Alicia")
        self.assertEqual(self.record.name.value, "Alicia")
        with self.assertRaises(ValueError):
            self.record.edit_name("")
        self.assertEqual(self.record.name.value, "Alicia")

    def test_add_birthday_replaces_previous(self):
        self.assertFalse(self.record.add_birthday("05.03.1990"))
        self.assertTrue(self.record.add_birthday("06.03.1991"))
        self.assertEqual(self.record.birthday.value, dt.date(1991, 3, 6))

    def test_invalid_birthday_keeps_previous(self):
        self.record.add_birthday("05.03.1990")
        with self.assertRaises(ValueError):
            self.record.add_birthday("nope")
        self.assertEqual(str(self.record.birthday), "05.03.1990")

    def test_matches_any_field(self):
        self.record.add_phone("0501234567")
        self.record.add_email("alice@example.com")
        self.record.add_address("Kyiv, Main st 1")
        self.record.add_birthday("05.03.1990")
        for text in ["ali", "ALICE@EXAMPLE", "main st", "05.03", "0501234567", "050 123", "+38050", "380501"]:
            with self.subTest(text=text):
                self.assertTrue(self.record.matches(text))
        for text in ["", "   ", "bob", "0509999999", "Lviv"]:
            with self.subTest(text=text):
                self.assertFalse(self.record.matches(text))

    def test_text_with_letters_is_not_matched_by_digits(self):
        self.record.add_phone("0501234567")
        self.assertFalse(self.record.matches("John 5"))

    def test_str(self):
        self.assertEqual(
            str(self.record),
            "Contact name: Alice, phones: , emails: , addresses: , birthday: -",
        )
        self.record.add_phone("0501234567")
        self.record.add_email("a@b.com")
        self.record.add_address("Kyiv")
        self.record.add_birthday("05.03.1990")
        self.assertEqual(
            str(self.record),
            "Contact name: Alice, phones: +380501234567, emails: a@b.com, "
            "addresses: Kyiv, birthday: 05.03.1990",
        )


if __name__ == "__main__":
    unittest.main()
