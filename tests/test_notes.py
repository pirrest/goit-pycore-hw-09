import unittest

from personal_assistant.notes import Note, NoteBook, Tag


class TagTest(unittest.TestCase):
    def test_normalizes_tag(self):
        self.assertEqual(Tag("#Shop").value, "shop")
        self.assertEqual(str(Tag("shop")), "#shop")

    def test_rejects_invalid_tags(self):
        for value in ["", "#", "two words", "a#b", None]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Tag(value)


class NoteTest(unittest.TestCase):
    def test_creates_note_with_deduplicated_tags(self):
        note = Note("Milk", "Buy 2 liters", ["#shop", "SHOP", "home"])
        self.assertEqual([t.value for t in note.tags], ["shop", "home"])
        self.assertIsNotNone(note.created_at)

    def test_rejects_empty_title_and_text(self):
        with self.assertRaises(ValueError):
            Note("", "text")
        with self.assertRaises(ValueError):
            Note("title", "  ")

    def test_edit_keeps_previous_value_on_error(self):
        note = Note("Milk", "Buy")
        note.edit_title("Bread")
        note.edit_text("Buy a loaf")
        with self.assertRaises(ValueError):
            note.edit_title("")
        self.assertEqual((note.title.value, note.text.value), ("Bread", "Buy a loaf"))

    def test_tags(self):
        note = Note("Milk", "Buy")
        self.assertTrue(note.add_tag("shop"))
        self.assertFalse(note.add_tag("#SHOP"))
        self.assertTrue(note.has_tag("#shop"))
        self.assertTrue(note.remove_tag("Shop"))
        self.assertFalse(note.remove_tag("shop"))
        with self.assertRaises(ValueError):
            note.add_tag("two words")

    def test_matches_title_and_text_ignoring_case(self):
        note = Note("Milk", "Buy 2 liters")
        self.assertTrue(note.matches("MILK"))
        self.assertTrue(note.matches("liters"))
        self.assertFalse(note.matches("bread"))
        self.assertFalse(note.matches(" "))

    def test_str(self):
        note = Note("Milk", "Buy", ["shop"])
        self.assertRegex(str(note), r"^Milk: Buy \[#shop\] \(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}\)$")


class NoteBookTest(unittest.TestCase):
    def setUp(self):
        self.book = NoteBook()
        self.milk = Note("Milk", "Buy 2 liters", ["shop", "home"])
        self.plan = Note("Plan", "Buy a gift", ["shop"])
        self.idle = Note("Idle", "Nothing")
        for note in (self.milk, self.plan, self.idle):
            self.book.add_note(note)

    def test_search(self):
        self.assertEqual(self.book.search("buy"), [self.milk, self.plan])
        self.assertEqual(self.book.search("zzz"), [])

    def test_find_by_tag(self):
        self.assertEqual(self.book.find_by_tag("#SHOP"), [self.milk, self.plan])
        self.assertEqual(self.book.find_by_tag("missing"), [])

    def test_group_by_tag_lists_multi_tag_notes_in_each_group(self):
        groups = self.book.group_by_tag()
        self.assertEqual(list(groups), ["home", "shop"])
        self.assertEqual(groups["home"], [self.milk])
        self.assertEqual(groups["shop"], [self.milk, self.plan])
        self.assertEqual(self.book.untagged(), [self.idle])

    def test_delete(self):
        self.assertTrue(self.book.delete(self.plan))
        self.assertFalse(self.book.delete(self.plan))
        self.assertEqual(list(self.book), [self.milk, self.idle])


if __name__ == "__main__":
    unittest.main()
