import os
import pickle


class AddressBookStorage:
    """Saves an address book to a file and loads it back using pickle."""

    DEFAULT_FILENAME = "addressbook.pkl"
    BACKUP_SUFFIX = ".bak"

    def __init__(self, filename: str = DEFAULT_FILENAME):
        self.filename = filename

    def save(self, book) -> None:
        """Write the address book to the file, replacing its previous content."""
        with open(self.filename, "wb") as f:
            pickle.dump(book, f)

    def load(self):
        """Read the address book from the file.

        A file that cannot be unpickled is renamed with the backup suffix, so the
        next save does not overwrite it.

        Returns:
            The stored address book, or None if the file is missing or corrupted.
        """
        try:
            with open(self.filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None
        except (pickle.UnpicklingError, EOFError, AttributeError, ImportError, IndexError):
            backup = self.filename + self.BACKUP_SUFFIX
            os.replace(self.filename, backup)
            print(f"Could not read {self.filename}, it was moved to {backup}. Starting with an empty address book.")
            return None
