import datetime as dt
import unittest
from unittest.mock import patch

from bot.bot import Bot, parse_input
from tests.test_address_book import make_fake_date


class BotTest(unittest.TestCase):
    def setUp(self):
        self.bot = Bot()

    def test_parse_input(self):
        self.assertEqual(parse_input("  ADD Alice 0501234567 "), ("add", ["Alice", "0501234567"]))
        self.assertEqual(parse_input("   "), ("", []))

    def test_add_contact(self):
        self.assertEqual(self.bot.add_contact(["Alice", "0501234567"]), "Contact added.")
        self.assertEqual(self.bot.add_contact(["alice", "0507654321"]), "Contact updated.")
        self.assertEqual(
            self.bot.add_contact(["Alice", "0507654321"]), "Phone already exists for Alice."
        )
        self.assertEqual(self.bot.add_contact(["Bob", "0501111111", "extra"]), "Contact added.")

    def test_add_contact_errors(self):
        self.assertEqual(self.bot.add_contact(["Alice"]), "Give me name and phone please.")
        self.assertEqual(
            self.bot.add_contact(["Alice", "123"]), "Phone number must consist of 10 digits."
        )
        self.assertEqual(self.bot.show_all([]), "No contacts.")  # nothing was left behind

    def test_change_contact(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.bot.add_contact(["Alice", "0507654321"])
        self.assertEqual(
            self.bot.change_contact(["Alice", "0501234567", "0509999999"]), "Contact updated."
        )
        self.assertEqual(self.bot.show_phone(["Alice"]), "0509999999; 0507654321")
        self.assertEqual(
            self.bot.change_contact(["Alice", "0000000000", "0501111111"]),
            "Phone 0000000000 not found for Alice.",
        )
        self.assertEqual(
            self.bot.change_contact(["Alice", "0509999999", "0507654321"]),
            "Phone 0507654321 already exists for Alice.",
        )
        self.assertEqual(
            self.bot.change_contact(["Bob", "0501234567", "0509999999"]), "Contact not found."
        )
        self.assertEqual(
            self.bot.change_contact(["Alice", "0509999999"]),
            "Give me name, old phone and new phone please.",
        )

    def test_show_phone_errors(self):
        self.assertEqual(self.bot.show_phone([]), "Enter user name.")
        self.assertEqual(self.bot.show_phone(["Bob"]), "Contact not found.")

    def test_birthday_commands(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(self.bot.show_birthday(["Alice"]), "Birthday is not set for Alice.")
        self.assertEqual(self.bot.add_birthday(["Alice", "05.03.1990"]), "Birthday added.")
        self.assertEqual(self.bot.add_birthday(["Alice", "06.03.1991"]), "Birthday updated.")
        self.assertEqual(self.bot.show_birthday(["Alice"]), "06.03.1991")
        self.assertIn("birthday: 06.03.1991", self.bot.show_all([]))

    def test_birthday_command_errors(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(
            self.bot.add_birthday(["Alice", "1990-03-05"]), "Invalid date format. Use DD.MM.YYYY"
        )
        self.assertEqual(self.bot.add_birthday(["Bob", "05.03.1990"]), "Contact not found.")
        self.assertEqual(
            self.bot.add_birthday(["Alice"]), "Give me name and birthday (DD.MM.YYYY) please."
        )
        self.assertEqual(self.bot.show_birthday([]), "Enter user name.")
        self.assertEqual(self.bot.show_birthday(["Bob"]), "Contact not found.")

    def test_birthdays(self):
        self.assertEqual(self.bot.birthdays([]), "No birthdays in the next 7 days.")
        self.bot.add_contact(["Alice", "0501234567"])
        self.bot.add_birthday(["Alice", "24.10.1990"])
        # 2026-10-24 is a Saturday, so the congratulation moves to Monday
        with patch("address_book.address_book.date", make_fake_date(dt.date(2026, 10, 23))):
            self.assertEqual(self.bot.birthdays([]), "Congratulate Alice on 26.10.2026 (Mon)")

    def test_run_loop(self):
        inputs = ["hello", "add Alice 0501234567", "bogus", "all", "exit"]
        with patch("builtins.input", side_effect=inputs), patch("builtins.print") as printed:
            self.bot.run()
        output = "\n".join(str(call.args[0]) for call in printed.call_args_list)
        self.assertIn("Welcome to the assistant bot!", output)
        self.assertIn("Contact added.", output)
        self.assertIn("Unknown command.", output)
        self.assertIn("Contact name: Alice", output)
        self.assertTrue(output.endswith("Good bye!"))


if __name__ == "__main__":
    unittest.main()
