import datetime as dt
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from personal_assistant.address_book import Record
from personal_assistant.bot.bot import Bot, parse_input
from tests.test_address_book import make_fake_date


class BotTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = Bot()

    def call(self, handler, args, answers=()):
        """Run a handler with the given console answers; return its result and the printed text."""
        out = StringIO()
        with patch("builtins.input", side_effect=list(answers)) as mocked_input, redirect_stdout(out):
            result = handler(args)
        self.assertEqual(mocked_input.call_count, len(answers), "unused or missing answers")
        return result, out.getvalue()

    def run_handler(self, handler, args, answers=()):
        return self.call(handler, args, answers)[0]

    def phones(self, index=0):
        return [p.value for p in self.bot.book[index].phones]


class ParseInputTest(unittest.TestCase):
    def test_parse_input(self):
        self.assertEqual(parse_input("  ADD Alice 0501234567 "), ("add", ["Alice", "0501234567"]))
        self.assertEqual(parse_input("   "), ("", []))

    def test_quotes_group_words(self):
        self.assertEqual(
            parse_input('add-note "Buy milk" "it\'s #1" #shop'),
            ("add-note", ["Buy milk", "it's #1", "#shop"]),
        )

    def test_unclosed_quote_is_an_error(self):
        with self.assertRaises(ValueError):
            parse_input('add "Alice')


class ContactsTest(BotTestCase):
    def test_add_contact(self):
        self.assertEqual(self.run_handler(self.bot.add_contact, ["Alice", "0501234567"]), "Contact added.")
        self.assertEqual(self.phones(), ["+380501234567"])

    def test_add_contact_without_phone(self):
        self.assertEqual(self.run_handler(self.bot.add_contact, ["Alice"]), "Contact added.")
        self.assertEqual(self.phones(), [])

    def test_add_contact_asks_for_missing_arguments(self):
        self.assertEqual(self.run_handler(self.bot.add_contact, [], ["Alice", "050 123 45 67"]), "Contact added.")
        self.assertEqual(self.phones(), ["+380501234567"])
        self.assertEqual(self.run_handler(self.bot.add_contact, [], ["Bob", ""]), "Contact added.")
        self.assertEqual(len(self.bot.book), 2)

    def test_add_contact_with_existing_name_can_add_phone_to_it(self):
        self.bot.add_contact(["Alice", "0501234567"])
        result, printed = self.call(self.bot.add_contact, ["alice", "0507654321"], ["1"])
        self.assertEqual(result, "Contact updated.")
        self.assertIn("1. Add the phone to the existing contact", printed)
        self.assertEqual(len(self.bot.book), 1)
        self.assertEqual(self.phones(), ["+380501234567", "+380507654321"])

    def test_add_contact_with_existing_name_can_create_new_one(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(self.run_handler(self.bot.add_contact, ["Alice", "0507654321"], ["2"]), "Contact added.")
        self.assertEqual(len(self.bot.book), 2)
        self.assertEqual(self.phones(1), ["+380507654321"])

    def test_add_contact_with_existing_name_can_be_cancelled(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(self.run_handler(self.bot.add_contact, ["Alice", "0507654321"], [""]), "Cancelled.")
        self.assertEqual(len(self.bot.book), 1)

    def test_add_phone_to_existing_contact_picks_among_same_names(self):
        self.bot.add_contact(["Alice"])
        self.bot.book.add_record(Record("Alice"))
        result = self.run_handler(self.bot.add_contact, ["Alice", "0501234567"], ["1", "2"])
        self.assertEqual(result, "Contact updated.")
        self.assertEqual(self.phones(0), [])
        self.assertEqual(self.phones(1), ["+380501234567"])

    def test_add_contact_without_phone_and_existing_name_asks_to_confirm(self):
        self.bot.add_contact(["Alice"])
        self.assertEqual(self.run_handler(self.bot.add_contact, ["Alice"], ["y"]), "Contact added.")
        self.assertEqual(len(self.bot.book), 2)
        self.assertEqual(self.run_handler(self.bot.add_contact, ["Alice"], ["n"]), "Cancelled.")
        self.assertEqual(len(self.bot.book), 2)

    def test_add_contact_with_invalid_phone_changes_nothing(self):
        self.assertEqual(
            self.run_handler(self.bot.add_contact, ["Alice", "123"]),
            "Invalid phone number. Use 0501234567 or +<country code><number>.",
        )
        self.assertEqual(self.run_handler(self.bot.show_all, []), "No contacts.")

    def test_add_phone(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(self.run_handler(self.bot.add_phone, ["Alice", "0507654321"]), "Phone added.")
        self.assertEqual(
            self.run_handler(self.bot.add_phone, ["Alice", "0507654321"]), "Phone already exists for Alice."
        )
        self.assertEqual(self.run_handler(self.bot.add_phone, ["Alice", "12"], []).startswith("Invalid phone"), True)
        self.assertEqual(self.run_handler(self.bot.add_phone, ["Bob", "0507654321"]), "Contact not found.")

    def test_selection_among_several_contacts(self):
        self.bot.add_contact(["Alice"])
        self.bot.add_contact(["Alicia"])
        result, printed = self.call(self.bot.add_phone, ["Ali", "0501234567"], ["2"])
        self.assertEqual(result, "Phone added.")
        self.assertIn("1. Contact name: Alice", printed)
        self.assertIn("2. Contact name: Alicia", printed)
        self.assertEqual(self.phones(1), ["+380501234567"])

    def test_exact_name_wins_over_partial_matches(self):
        self.bot.add_contact(["Anna"])
        self.bot.add_contact(["Ann"])
        self.assertEqual(self.run_handler(self.bot.add_phone, ["Ann", "0501234567"]), "Phone added.")
        self.assertEqual(self.phones(1), ["+380501234567"])

    def test_selection_can_be_cancelled(self):
        self.bot.add_contact(["Alice"])
        self.bot.add_contact(["Alicia"])
        self.assertEqual(self.run_handler(self.bot.add_phone, ["Ali", "0501234567"], [""]), "Cancelled.")
        self.assertEqual(self.phones(0), [])
        self.assertEqual(self.phones(1), [])

    def test_change_phone(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.bot.add_phone(["Alice", "0507654321"])
        self.assertEqual(
            self.run_handler(self.bot.change_phone, ["Alice", "0501234567", "0509999999"]), "Phone updated."
        )
        self.assertEqual(self.phones(), ["+380509999999", "+380507654321"])
        self.assertEqual(
            self.run_handler(self.bot.change_phone, ["Alice", "0000000000", "0501111111"]),
            "Phone 0000000000 not found for Alice.",
        )
        self.assertEqual(
            self.run_handler(self.bot.change_phone, ["Alice", "0509999999", "0507654321"]),
            "Phone 0507654321 already exists for Alice.",
        )
        self.assertEqual(
            self.run_handler(self.bot.change_phone, ["Bob", "0501234567", "0509999999"]), "Contact not found."
        )

    def test_change_phone_asks_which_one_and_the_new_value(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.bot.add_phone(["Alice", "0507654321"])
        self.assertEqual(self.run_handler(self.bot.change_phone, ["Alice"], ["2", "0509999999"]), "Phone updated.")
        self.assertEqual(self.phones(), ["+380501234567", "+380509999999"])

    def test_change_phone_without_phones(self):
        self.bot.add_contact(["Alice"])
        self.assertEqual(self.run_handler(self.bot.change_phone, ["Alice"]), "Alice has no phones.")

    def test_remove_phone(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(self.run_handler(self.bot.remove_phone, ["Alice", "0501234567"]), "Phone removed.")
        self.assertEqual(self.phones(), [])

    def test_email_commands(self):
        self.bot.add_contact(["Alice"])
        self.assertEqual(self.run_handler(self.bot.add_email, ["Alice", "a@b.com"]), "Email added.")
        self.assertEqual(self.run_handler(self.bot.add_email, ["Alice", "A@B.com"]), "Email already exists for Alice.")
        self.assertEqual(self.run_handler(self.bot.add_email, ["Alice", "bad"]), "Invalid email. Use name@domain.com")
        self.assertEqual(self.run_handler(self.bot.change_email, ["Alice", "a@b.com", "c@d.com"]), "Email updated.")
        self.assertEqual([e.value for e in self.bot.book[0].emails], ["c@d.com"])
        self.assertEqual(self.run_handler(self.bot.remove_email, ["Alice", "c@d.com"]), "Email removed.")
        self.assertEqual(self.run_handler(self.bot.change_email, ["Alice"]), "Alice has no emails.")

    def test_address_commands(self):
        self.bot.add_contact(["Alice"])
        self.assertEqual(self.run_handler(self.bot.add_address, ["Alice", "Kyiv, Main st 1"]), "Address added.")
        self.assertEqual(self.run_handler(self.bot.add_address, ["Alice", "Lviv"]), "Address added.")
        self.assertEqual(self.run_handler(self.bot.change_address, ["Alice", "Lviv", "Odesa"]), "Address updated.")
        self.assertEqual([a.value for a in self.bot.book[0].addresses], ["Kyiv, Main st 1", "Odesa"])
        self.assertEqual(self.run_handler(self.bot.remove_address, ["Alice"], ["1"]), "Address removed.")
        self.assertEqual([a.value for a in self.bot.book[0].addresses], ["Odesa"])

    def test_change_name(self):
        self.bot.add_contact(["Alice"])
        self.assertEqual(self.run_handler(self.bot.change_name, ["Alice", "Alicia"]), "Name updated.")
        self.assertEqual(self.bot.book[0].name.value, "Alicia")

    def test_edit_contact(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(self.run_handler(self.bot.edit_contact, ["Alice"], ["1", "Alicia"]), "Name updated.")
        self.assertEqual(
            self.run_handler(self.bot.edit_contact, ["Alicia"], ["2", "0509999999"]), "Phone updated."
        )
        self.assertEqual(self.phones(), ["+380509999999"])
        self.assertEqual(self.run_handler(self.bot.edit_contact, ["Alicia"], ["5", "05.03.1990"]), "Birthday added.")
        self.assertEqual(self.run_handler(self.bot.edit_contact, ["Alicia"], ["5", "06.03.1990"]), "Birthday updated.")
        self.assertEqual(self.run_handler(self.bot.edit_contact, ["Alicia"], ["3"]), "Alicia has no emails.")

    def test_delete_contact(self):
        self.bot.add_contact(["Alice"])
        self.assertEqual(self.run_handler(self.bot.delete_contact, ["Alice"], ["n"]), "Cancelled.")
        self.assertEqual(len(self.bot.book), 1)
        self.assertEqual(self.run_handler(self.bot.delete_contact, ["Alice"], ["y"]), "Contact deleted.")
        self.assertEqual(len(self.bot.book), 0)
        self.assertEqual(self.run_handler(self.bot.delete_contact, ["Alice"]), "Contact not found.")

    def test_delete_contact_removes_only_the_chosen_one(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.run_handler(self.bot.add_contact, ["Alice", "0507654321"], ["2"])
        self.assertEqual(self.run_handler(self.bot.delete_contact, ["Alice"], ["1", "y"]), "Contact deleted.")
        self.assertEqual(self.phones(), ["+380507654321"])

    def test_show_phone(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(self.run_handler(self.bot.show_phone, ["Alice"]), "+380501234567")
        self.assertEqual(self.run_handler(self.bot.show_phone, ["Bob"]), "Contact not found.")
        self.bot.add_contact(["Carl"])
        self.assertEqual(self.run_handler(self.bot.show_phone, ["Carl"]), "No phones.")

    def test_show_phone_asks_for_name(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(self.run_handler(self.bot.show_phone, [], ["Alice"]), "+380501234567")
        self.assertEqual(self.run_handler(self.bot.show_phone, [], [""]), "The value cannot be empty.")

    def test_search_contacts(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.bot.add_contact(["Bob", "0507654321"])
        self.bot.add_email(["Bob", "bob@alice.org"])
        self.assertEqual(
            self.run_handler(self.bot.search_contacts, ["alice"]).splitlines()[0][:25], "1. Contact name: Alice, p"
        )
        self.assertEqual(len(self.run_handler(self.bot.search_contacts, ["alice"]).splitlines()), 2)
        self.assertEqual(len(self.run_handler(self.bot.search_contacts, ["050", "765"]).splitlines()), 1)
        self.assertEqual(self.run_handler(self.bot.search_contacts, ["zzz"]), "No contacts found.")

    def test_birthday_commands(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(self.run_handler(self.bot.show_birthday, ["Alice"]), "Birthday is not set for Alice.")
        self.assertEqual(self.run_handler(self.bot.add_birthday, ["Alice", "05.03.1990"]), "Birthday added.")
        self.assertEqual(self.run_handler(self.bot.add_birthday, ["Alice", "06.03.1991"]), "Birthday updated.")
        self.assertEqual(self.run_handler(self.bot.show_birthday, ["Alice"]), "06.03.1991")
        self.assertIn("birthday: 06.03.1991", self.run_handler(self.bot.show_all, []))

    def test_birthday_command_errors(self):
        self.bot.add_contact(["Alice", "0501234567"])
        self.assertEqual(
            self.run_handler(self.bot.add_birthday, ["Alice", "1990-03-05"]), "Invalid date format. Use DD.MM.YYYY"
        )
        self.assertEqual(self.run_handler(self.bot.add_birthday, ["Bob", "05.03.1990"]), "Contact not found.")

    def test_birthdays(self):
        self.assertEqual(self.run_handler(self.bot.birthdays, []), "No birthdays in the next 7 days.")
        self.bot.add_contact(["Alice", "0501234567"])
        self.bot.add_birthday(["Alice", "24.10.1990"])
        self.bot.add_contact(["Bob"])
        self.bot.add_birthday(["Bob", "28.10.1990"])
        with patch("personal_assistant.address_book.address_book.date", make_fake_date(dt.date(2026, 10, 23))):
            # Saturday is moved to Monday, so the real birthday is shown too
            self.assertEqual(
                self.run_handler(self.bot.birthdays, []),
                "Congratulate Alice on 26.10.2026 (Mon), birthday on 24.10.2026 (Sat)\n"
                "Congratulate Bob on 28.10.2026 (Wed)",
            )
            self.assertEqual(
                self.run_handler(self.bot.birthdays, ["1"]), "No birthdays in the next 1 days."
            )
            self.assertEqual(
                self.run_handler(self.bot.birthdays, ["2"]),
                "Congratulate Alice on 26.10.2026 (Mon), birthday on 24.10.2026 (Sat)",
            )

    def test_birthdays_rejects_bad_days(self):
        for value in ["0", "-1", "abc", "1.5"]:
            with self.subTest(value=value):
                self.assertEqual(self.run_handler(self.bot.birthdays, [value]), "Days must be a positive integer.")


class NotesTest(BotTestCase):
    def add_notes(self):
        self.bot.add_note(["Milk", "Buy 2 liters", "#shop", "home"])
        self.bot.add_note(["Plan", "Buy a gift", "shop"])
        self.bot.add_note(["Idle", "Nothing"])

    def test_add_note_with_tags(self):
        self.assertEqual(self.run_handler(self.bot.add_note, ["Milk", "Buy 2 liters", "#shop", "home"]), "Note added.")
        note = self.bot.notes[0]
        self.assertEqual((note.title.value, note.text.value), ("Milk", "Buy 2 liters"))
        self.assertEqual([t.value for t in note.tags], ["shop", "home"])

    def test_add_note_asks_for_missing_arguments(self):
        self.assertEqual(self.run_handler(self.bot.add_note, [], ["Milk", "Buy", "shop #home"]), "Note added.")
        self.assertEqual([t.value for t in self.bot.notes[0].tags], ["shop", "home"])
        self.assertEqual(self.run_handler(self.bot.add_note, ["Plan"], ["Do it", ""]), "Note added.")
        self.assertEqual(self.bot.notes[1].tags, [])
        # Tags are not asked for when both the title and the text are given
        self.assertEqual(self.run_handler(self.bot.add_note, ["Idle", "Nothing"]), "Note added.")

    def test_add_note_errors(self):
        self.assertEqual(self.run_handler(self.bot.add_note, ["", "text", "x"]), "The value cannot be empty.")
        self.assertEqual(len(self.bot.notes), 0)

    def test_show_and_search_notes(self):
        self.assertEqual(self.run_handler(self.bot.show_notes, []), "No notes.")
        self.add_notes()
        self.assertEqual(len(self.run_handler(self.bot.show_notes, []).splitlines()), 3)
        self.assertEqual(len(self.run_handler(self.bot.search_notes, ["BUY"]).splitlines()), 2)
        self.assertEqual(self.run_handler(self.bot.search_notes, ["zzz"]), "No notes found.")

    def test_search_by_tag(self):
        self.add_notes()
        self.assertEqual(len(self.run_handler(self.bot.search_notes_by_tag, ["#SHOP"]).splitlines()), 2)
        self.assertEqual(len(self.run_handler(self.bot.search_notes_by_tag, ["home"]).splitlines()), 1)
        self.assertEqual(self.run_handler(self.bot.search_notes_by_tag, ["none"]), "No notes found.")

    def test_sort_by_tags_groups_notes(self):
        self.assertEqual(self.run_handler(self.bot.sort_notes_by_tags, []), "No notes.")
        self.add_notes()
        lines = self.run_handler(self.bot.sort_notes_by_tags, []).splitlines()
        headers = [line for line in lines if not line.startswith(" ")]
        self.assertEqual(headers, ["#home", "#shop", "(no tags)"])
        self.assertEqual(sum(line.startswith("  Milk") for line in lines), 2)

    def test_edit_note(self):
        self.add_notes()
        self.assertEqual(self.run_handler(self.bot.edit_note, ["milk"], ["1", "Bread"]), "Title updated.")
        self.assertEqual(self.run_handler(self.bot.edit_note, ["bread"], ["2", "Buy a loaf"]), "Text updated.")
        self.assertEqual((self.bot.notes[0].title.value, self.bot.notes[0].text.value), ("Bread", "Buy a loaf"))
        self.assertEqual(self.run_handler(self.bot.edit_note, ["zzz"]), "Note not found.")

    def test_edit_note_picks_among_several(self):
        self.add_notes()
        self.assertEqual(self.run_handler(self.bot.edit_note, ["buy"], ["2", "1", "Gift"]), "Title updated.")
        self.assertEqual(self.bot.notes[1].title.value, "Gift")

    def test_add_and_remove_tags(self):
        self.add_notes()
        self.assertEqual(self.run_handler(self.bot.add_tag, ["idle", "#todo", "urgent"]), "Tags added.")
        self.assertEqual([t.value for t in self.bot.notes[2].tags], ["todo", "urgent"])
        self.assertEqual(self.run_handler(self.bot.add_tag, ["idle", "todo"]), "Note already has these tags.")
        self.assertEqual(self.run_handler(self.bot.add_tag, ["idle"], ["more"]), "Tags added.")
        self.assertEqual(self.run_handler(self.bot.remove_tag, ["idle", "#TODO"]), "Tag removed.")
        self.assertEqual(self.run_handler(self.bot.remove_tag, ["idle"], ["1"]), "Tag removed.")
        self.assertEqual([t.value for t in self.bot.notes[2].tags], ["more"])
        self.assertEqual(self.run_handler(self.bot.remove_tag, ["idle", "nope"]), "Tag nope not found in the note.")
        self.run_handler(self.bot.remove_tag, ["idle", "more"])
        self.assertEqual(self.run_handler(self.bot.remove_tag, ["idle"]), "The note has no tags.")

    def test_delete_note(self):
        self.add_notes()
        self.assertEqual(self.run_handler(self.bot.delete_note, ["milk"], ["n"]), "Cancelled.")
        self.assertEqual(len(self.bot.notes), 3)
        self.assertEqual(self.run_handler(self.bot.delete_note, ["milk"], ["y"]), "Note deleted.")
        self.assertEqual([n.title.value for n in self.bot.notes], ["Plan", "Idle"])


class RunLoopTest(BotTestCase):
    def run_loop(self, inputs):
        with patch("builtins.input", side_effect=inputs), patch("builtins.print") as printed:
            self.bot.run()
        return "\n".join(str(call.args[0]) for call in printed.call_args_list)

    def test_run_loop(self):
        output = self.run_loop(["hello", "add Alice 0501234567", "bogus", "all", "exit"])
        self.assertIn("Welcome to the assistant bot!", output)
        self.assertIn("Contact added.", output)
        self.assertIn("Unknown command.", output)
        self.assertIn("Contact name: Alice", output)
        self.assertTrue(output.endswith("Good bye!"))

    def test_all_list_and_contacts_show_the_same_contacts(self):
        self.bot.add_contact(["Alice", "0501234567"])
        outputs = {self.bot.commands[name]([]) for name in ("all", "list", "contacts")}
        self.assertEqual(len(outputs), 1)
        self.assertIn("Contact name: Alice", outputs.pop())

    def test_run_loop_handles_quotes_and_interactive_prompts(self):
        output = self.run_loop(['add-note "Buy milk" "2 liters" shop', "add Bob", "add-email", "bob", "b@c.com", "all-notes", "exit"])
        self.assertIn("Note added.", output)
        self.assertIn("Email added.", output)
        self.assertIn("1. Buy milk: 2 liters [#shop]", output)

    def test_run_loop_reports_unclosed_quote(self):
        output = self.run_loop(['add "Alice', "exit"])
        self.assertIn("Invalid input: a double quote is not closed.", output)
        self.assertEqual(len(self.bot.book), 0)

    def test_run_loop_stops_on_end_of_input_inside_a_prompt(self):
        output = self.run_loop(["add", EOFError()])
        self.assertTrue(output.endswith("Good bye!"))


if __name__ == "__main__":
    unittest.main()
