import os
import pickle


class FileStorage:
    """Saves an object to a file and loads it back using pickle."""

    DIRECTORY_NAME = ".personal_assistant"
    BACKUP_SUFFIX = ".bak"

    def __init__(self, filename: str):
        self.filename = filename

    @classmethod
    def default_path(cls, name: str) -> str:
        """Return the path of a data file in the assistant folder inside the user's home."""
        return os.path.join(os.path.expanduser("~"), cls.DIRECTORY_NAME, name)

    def save(self, data) -> None:
        """Write the object to the file, replacing its previous content.

        Missing parent folders are created.
        """
        os.makedirs(os.path.dirname(self.filename) or ".", exist_ok=True)
        with open(self.filename, "wb") as f:
            pickle.dump(data, f)

    def load(self):
        """Read the object from the file.

        A file that cannot be unpickled is renamed with the backup suffix, so the
        next save does not overwrite it.

        Returns:
            The stored object, or None if the file is missing or corrupted.
        """
        try:
            with open(self.filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None
        except (pickle.UnpicklingError, EOFError, AttributeError, ImportError, IndexError):
            backup = self.filename + self.BACKUP_SUFFIX
            os.replace(self.filename, backup)
            print(f"Could not read {self.filename}, it was moved to {backup}. Starting with empty data.")
            return None
