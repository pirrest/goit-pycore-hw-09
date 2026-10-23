import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

from address_book import AddressBook, AddressBookStorage, Record


class AddressBookStorageTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.filename = os.path.join(tmp.name, "book.pkl")

    def make_book(self) -> AddressBook:
        book = AddressBook()
        alice = Record("Alice")
        alice.add_phone("1234567890")
        alice.add_phone("0987654321")
        alice.add_birthday("15.03.1990")
        book.add_record(alice)
        book.add_record(Record("Bob"))
        return book

    def test_save_and_load_keeps_records(self):
        self.make_book().save(self.filename)

        loaded = AddressBook.load(self.filename)

        self.assertIsInstance(loaded, AddressBook)
        self.assertEqual(set(loaded.keys()), {"alice", "bob"})
        alice = loaded.find("alice")
        self.assertEqual([p.value for p in alice.phones], ["1234567890", "0987654321"])
        self.assertEqual(str(alice.birthday), "15.03.1990")
        self.assertIsNone(loaded.find("bob").birthday)

    def test_loaded_book_is_usable(self):
        self.make_book().save(self.filename)

        loaded = AddressBook.load(self.filename)

        self.assertFalse(loaded.add_record(Record("ALICE")))
        self.assertTrue(loaded.delete("bob"))

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
        backup = self.filename + AddressBookStorage.BACKUP_SUFFIX
        with open(backup, "rb") as f:
            self.assertEqual(f.read(), b"not a pickle")
        self.assertIn("moved to", out.getvalue())

    def test_load_empty_file_moves_it_to_backup(self):
        open(self.filename, "wb").close()

        with redirect_stdout(StringIO()):
            loaded = AddressBook.load(self.filename)

        self.assertEqual(len(loaded), 0)
        self.assertTrue(os.path.exists(self.filename + AddressBookStorage.BACKUP_SUFFIX))

    def test_save_overwrites_previous_content(self):
        self.make_book().save(self.filename)
        AddressBook().save(self.filename)

        self.assertEqual(len(AddressBook.load(self.filename)), 0)

    def test_storage_load_returns_none_for_missing_file(self):
        self.assertIsNone(AddressBookStorage(self.filename).load())


if __name__ == "__main__":
    unittest.main()
