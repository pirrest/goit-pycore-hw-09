import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from address_book import AddressBook, Record
from notes import Note, NoteBook
from storage import FileStorage


class FileStorageTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.directory = tmp.name
        self.filename = os.path.join(tmp.name, "book.pkl")

    def make_book(self) -> AddressBook:
        book = AddressBook()
        alice = Record("Alice")
        alice.add_phone("0501234567")
        alice.add_phone("0987654321")
        alice.add_email("alice@example.com")
        alice.add_address("Kyiv")
        alice.add_birthday("15.03.1990")
        book.add_record(alice)
        book.add_record(Record("Bob"))
        return book

    def test_save_and_load_keeps_records(self):
        self.make_book().save(self.filename)

        loaded = AddressBook.load(self.filename)

        self.assertIsInstance(loaded, AddressBook)
        self.assertEqual([r.name.value for r in loaded], ["Alice", "Bob"])
        alice = loaded[0]
        self.assertEqual([p.value for p in alice.phones], ["+380501234567", "+380987654321"])
        self.assertEqual([e.value for e in alice.emails], ["alice@example.com"])
        self.assertEqual([a.value for a in alice.addresses], ["Kyiv"])
        self.assertEqual(str(alice.birthday), "15.03.1990")
        self.assertIsNone(loaded[1].birthday)

    def test_loaded_book_is_usable(self):
        self.make_book().save(self.filename)

        loaded = AddressBook.load(self.filename)

        self.assertEqual(len(loaded.find_by_name("alice", exact=True)), 1)
        self.assertTrue(loaded.delete(loaded[1]))

    def test_notes_are_saved_with_the_same_storage(self):
        notes = NoteBook()
        notes.add_note(Note("Milk", "Buy 2 liters", ["shop"]))
        notes.save(self.filename)

        loaded = NoteBook.load(self.filename)

        self.assertIsInstance(loaded, NoteBook)
        self.assertEqual(str(loaded[0].title), "Milk")
        self.assertTrue(loaded[0].has_tag("shop"))

    def test_load_missing_file_returns_empty_book(self):
        loaded = AddressBook.load(self.filename)

        self.assertIsInstance(loaded, AddressBook)
        self.assertEqual(len(loaded), 0)

    def test_load_corrupted_file_moves_it_to_backup(self):
        with open(self.filename, "wb") as f:
            f.write(b"not a pickle")

        with redirect_stdout(StringIO()) as out:
            loaded = AddressBook.load(self.filename)

        self.assertEqual(len(loaded), 0)
        self.assertFalse(os.path.exists(self.filename))
        with open(self.filename + FileStorage.BACKUP_SUFFIX, "rb") as f:
            self.assertEqual(f.read(), b"not a pickle")
        self.assertIn("moved to", out.getvalue())

    def test_load_empty_file_moves_it_to_backup(self):
        open(self.filename, "wb").close()

        with redirect_stdout(StringIO()):
            loaded = AddressBook.load(self.filename)

        self.assertEqual(len(loaded), 0)
        self.assertTrue(os.path.exists(self.filename + FileStorage.BACKUP_SUFFIX))

    def test_save_overwrites_previous_content(self):
        self.make_book().save(self.filename)
        AddressBook().save(self.filename)

        self.assertEqual(len(AddressBook.load(self.filename)), 0)

    def test_save_creates_missing_folders(self):
        filename = os.path.join(self.directory, "nested", "dir", "book.pkl")

        self.make_book().save(filename)

        self.assertEqual(len(AddressBook.load(filename)), 2)

    def test_storage_load_returns_none_for_missing_file(self):
        self.assertIsNone(FileStorage(self.filename).load())

    def test_default_files_live_in_the_assistant_folder_of_the_home(self):
        with patch.dict(os.environ, {"HOME": self.directory, "USERPROFILE": self.directory}):
            self.make_book().save()
            NoteBook().save()
            loaded = AddressBook.load()

        folder = os.path.join(self.directory, FileStorage.DIRECTORY_NAME)
        self.assertEqual(sorted(os.listdir(folder)), ["contacts.pkl", "notes.pkl"])
        self.assertEqual(len(loaded), 2)


if __name__ == "__main__":
    unittest.main()
