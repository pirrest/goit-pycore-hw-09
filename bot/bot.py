from functools import wraps

from address_book import AddressBook, Birthday, Record

HELP_TEXT = f"""Commands:
  hello | help                              - show this help
  add [name] [phone]                        - add a contact or a phone to an existing one
  change [name] [old phone] [new phone]     - change a contact's phone
  phone [name]                              - show a contact's phones
  all | list                                - show all contacts
  add-birthday [name] [DD.MM.YYYY]          - set a contact's birthday
  show-birthday [name]                      - show a contact's birthday
  birthdays                                 - show birthdays in the next {Birthday.UPCOMING_DAYS} days
  exit | close                              - quit"""


def input_error(func):
    """Turn input errors raised by a handler into user-friendly messages."""

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e) or "Give me name and phone please."
        except KeyError as e:
            # str(KeyError) wraps the text in quotes, so use the raw argument
            return (e.args[0] if e.args else "") or "Contact not found."
        except IndexError as e:
            return str(e) or "Enter the argument for the command."

    return inner


def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.strip().lower(), args


class Bot:
    """Console assistant bot working with an address book."""

    def __init__(self, book: AddressBook | None = None):
        self.book = AddressBook() if book is None else book
        self.commands = {
            "hello": self.hello,
            "help": self.hello,
            "add": self.add_contact,
            "change": self.change_contact,
            "phone": self.show_phone,
            "all": self.show_all,
            "list": self.show_all,
            "add-birthday": self.add_birthday,
            "show-birthday": self.show_birthday,
            "birthdays": self.birthdays,
        }

    def _get_record(self, name: str) -> Record:
        """Return the record with the given name or raise KeyError."""
        record = self.book.find(name)
        if record is None:
            raise KeyError("Contact not found.")
        return record

    def hello(self, args) -> str:
        return f"How can I help you?\n{HELP_TEXT}"

    @input_error
    def add_contact(self, args) -> str:
        if len(args) < 2:
            raise ValueError("Give me name and phone please.")
        name, phone, *_ = args
        record = self.book.find(name)
        is_new = record is None
        if is_new:
            record = Record(name)
        # Add the phone before the record goes to the book, so an invalid
        # phone does not leave an empty contact behind
        if not record.add_phone(phone):
            return f"Phone already exists for {record.name}."
        if is_new:
            self.book.add_record(record)
            return "Contact added."
        return "Contact updated."

    @input_error
    def change_contact(self, args) -> str:
        if len(args) != 3:
            raise ValueError("Give me name, old phone and new phone please.")
        name, old_phone, new_phone = args
        record = self._get_record(name)
        if not record.edit_phone(old_phone, new_phone):
            if record.find_phone(old_phone) is None:
                raise ValueError(f"Phone {old_phone} not found for {record.name}.")
            raise ValueError(f"Phone {new_phone} already exists for {record.name}.")
        return "Contact updated."

    @input_error
    def show_phone(self, args) -> str:
        if not args:
            raise IndexError("Enter user name.")
        record = self._get_record(args[0])
        return "; ".join(p.value for p in record.phones) or "No phones."

    @input_error
    def show_all(self, args) -> str:
        if not self.book:
            return "No contacts."
        return "\n".join(str(record) for record in self.book.values())

    @input_error
    def add_birthday(self, args) -> str:
        if len(args) != 2:
            raise ValueError("Give me name and birthday (DD.MM.YYYY) please.")
        name, birthday = args
        record = self._get_record(name)
        replaced = record.add_birthday(birthday)
        return "Birthday updated." if replaced else "Birthday added."

    @input_error
    def show_birthday(self, args) -> str:
        if not args:
            raise IndexError("Enter user name.")
        record = self._get_record(args[0])
        if record.birthday is None:
            return f"Birthday is not set for {record.name}."
        return str(record.birthday)

    @input_error
    def birthdays(self, args) -> str:
        upcoming = self.book.get_upcoming_birthdays()
        if not upcoming:
            return f"No birthdays in the next {Birthday.UPCOMING_DAYS} days."
        return "\n".join(
            f"Congratulate {item.record.name} on "
            f"{item.congratulation_date:%d.%m.%Y} ({item.congratulation_date:%a})"
            for item in upcoming
        )

    def run(self) -> None:
        """Read commands from the console until the user quits."""
        print("Welcome to the assistant bot!")
        while True:
            try:
                user_input = input("Enter a command: ")
            except (EOFError, KeyboardInterrupt):
                print("\nGood bye!")
                break
            command, args = parse_input(user_input)

            if command in ["close", "exit"]:
                print("Good bye!")
                break

            handler = self.commands.get(command)
            if handler is None:
                print("Unknown command.")
                print(HELP_TEXT)
            else:
                print(handler(args))


if __name__ == "__main__":
    Bot().run()
