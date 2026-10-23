import shlex
from dataclasses import dataclass
from functools import wraps

from address_book import AddressBook, Birthday, Record
from notes import Note, NoteBook

from .command_completer import CommandCompleter
from .prompt import Cancelled, ask, choose, confirm

HELP_TEXT = f"""Values with spaces go in double quotes. Missing arguments are asked for.
Contacts:
  add [name] [phone]                        - add a contact, or a phone to an existing one
  add-phone [name] [phone]                  - add a phone to a contact
  add-email [name] [email]                  - add an email to a contact
  add-address [name] [address]              - add an address to a contact
  add-birthday [name] [DD.MM.YYYY]          - set a contact's birthday
  change [name] [old phone] [new phone]     - change a contact's phone (alias: change-phone)
  change-email [name] [old] [new]           - change a contact's email
  change-address [name] [old] [new]         - change a contact's address
  change-name [name] [new name]             - rename a contact
  remove-phone | remove-email | remove-address [name] [value]
  edit-contact [name]                       - choose a field and edit it
  delete-contact [name]                     - delete a contact
  phone [name]                              - show a contact's phones
  show-birthday [name]                      - show a contact's birthday
  search [text]                             - find contacts by any field
  all | list | contacts                     - show all contacts
  birthdays [days]                          - show birthdays in the next days (default {Birthday.UPCOMING_DAYS})
Notes:
  add-note [title] [text] [tags...]         - add a note
  all-notes | notes                         - show all notes
  search-notes [text]                       - find notes by title or text
  search-notes-tag [tag]                    - find notes with a tag
  sort-notes-tags                           - show notes grouped by tag
  edit-note [text]                          - edit the title or the text of a note
  add-tag [note] [tags...]                  - add tags to a note
  remove-tag [note] [tag]                   - remove a tag from a note
  delete-note [note]                        - delete a note
Other:
  hello | help                              - show this help
  exit | close                              - quit"""

ADD_TO_EXISTING = "Add the phone to the existing contact"
CREATE_NEW = "Create a new contact"
CONTACT_FIELDS = ["Name", "Phone", "Email", "Address", "Birthday"]
NOTE_FIELDS = ["Title", "Text"]


@dataclass(frozen=True)
class ValueKind:
    """Names of a multi-valued record field and of its `Record` members."""

    singular: str
    plural: str
    items: str
    find: str
    add: str
    edit: str
    remove: str

    @property
    def title(self) -> str:
        return self.singular.capitalize()


PHONE = ValueKind("phone", "phones", "phones", "find_phone", "add_phone", "edit_phone", "remove_phone")
EMAIL = ValueKind("email", "emails", "emails", "find_email", "add_email", "edit_email", "remove_email")
ADDRESS = ValueKind(
    "address", "addresses", "addresses", "find_address", "add_address", "edit_address", "remove_address"
)


def input_error(func):
    """Turn input errors raised by a handler into user-friendly messages."""

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Cancelled:
            return "Cancelled."
        except ValueError as e:
            return str(e) or "Give me name and phone please."
        except KeyError as e:
            # str(KeyError) wraps the text in quotes, so use the raw argument
            return (e.args[0] if e.args else "") or "Contact not found."
        except IndexError as e:
            return str(e) or "Enter the argument for the command."

    return inner


def parse_input(user_input):
    """Split the input into a command and its arguments; double quotes group words.

    Raises:
        ValueError: If a quote is not closed.
    """
    lexer = shlex.shlex(user_input, posix=True)
    lexer.whitespace_split = True
    lexer.quotes = '"'
    lexer.commenters = ""
    lexer.escape = ""
    parts = list(lexer)
    if not parts:
        return "", []
    cmd, *args = parts
    return cmd.strip().lower(), args


def numbered(items) -> str:
    """Return the items as a numbered list."""
    return "\n".join(f"{number}. {item}" for number, item in enumerate(items, start=1))


class Bot:
    """Console assistant bot working with an address book and a note book."""

    def __init__(self, book: AddressBook | None = None, notes: NoteBook | None = None):
        self.book = AddressBook() if book is None else book
        self.notes = NoteBook() if notes is None else notes
        self.commands = {
            "hello": self.hello,
            "help": self.hello,
            "add": self.add_contact,
            "add-phone": self.add_phone,
            "add-email": self.add_email,
            "add-address": self.add_address,
            "add-birthday": self.add_birthday,
            "change": self.change_phone,
            "change-phone": self.change_phone,
            "change-email": self.change_email,
            "change-address": self.change_address,
            "change-name": self.change_name,
            "remove-phone": self.remove_phone,
            "remove-email": self.remove_email,
            "remove-address": self.remove_address,
            "edit-contact": self.edit_contact,
            "delete-contact": self.delete_contact,
            "phone": self.show_phone,
            "show-birthday": self.show_birthday,
            "search": self.search_contacts,
            "all": self.show_all,
            "list": self.show_all,
            "contacts": self.show_all,
            "birthdays": self.birthdays,
            "add-note": self.add_note,
            "all-notes": self.show_notes,
            "notes": self.show_notes,
            "search-notes": self.search_notes,
            "search-notes-tag": self.search_notes_by_tag,
            "sort-notes-tags": self.sort_notes_by_tags,
            "edit-note": self.edit_note,
            "add-tag": self.add_tag,
            "remove-tag": self.remove_tag,
            "delete-note": self.delete_note,
        }
        self.completer = CommandCompleter([*self.commands, "exit", "close"])

    @staticmethod
    def _arg(args, index: int, prompt: str) -> str:
        """Return the argument at the index, asking the user if it is missing."""
        value = args[index].strip() if index < len(args) else ask(prompt)
        if not value:
            raise ValueError("The value cannot be empty.")
        return value

    @staticmethod
    def _text_arg(args, prompt: str) -> str:
        """Return all arguments joined into one text, asking the user if there are none."""
        value = " ".join(args).strip() or ask(prompt)
        if not value:
            raise ValueError("The value cannot be empty.")
        return value

    def _select_record(self, args) -> Record:
        """Return the contact named by the first argument, asking to choose among several.

        Raises:
            KeyError: If no contact has such a name.
        """
        name = self._arg(args, 0, "Contact name: ")
        matches = self.book.find_by_name(name, exact=True) or self.book.find_by_name(name)
        if not matches:
            raise KeyError("Contact not found.")
        return choose(matches, header=f"Several contacts match '{name}':")

    def _select_note(self, args) -> Note:
        """Return the note found by the arguments, asking to choose among several.

        Raises:
            KeyError: If no note matches.
        """
        query = self._text_arg(args, "Part of the note title or text: ")
        matches = self.notes.search(query)
        if not matches:
            raise KeyError("Note not found.")
        return choose(matches, header=f"Several notes match '{query}':")

    @staticmethod
    def _pick_value(record: Record, kind: ValueKind, args, index: int):
        """Return the value given at the index of the arguments, or let the user choose one."""
        if not getattr(record, kind.items):
            raise ValueError(f"{record.name} has no {kind.plural}.")
        if index < len(args):
            item = getattr(record, kind.find)(args[index])
            if item is None:
                raise ValueError(f"{kind.title} {args[index]} not found for {record.name}.")
            return item
        return choose(getattr(record, kind.items), header=f"Choose the {kind.singular}:")

    def _add_value(self, kind: ValueKind, record: Record, args) -> str:
        value = self._arg(args, 0, f"{kind.title}: ")
        if not getattr(record, kind.add)(value):
            return f"{kind.title} already exists for {record.name}."
        return f"{kind.title} added."

    def _change_value(self, kind: ValueKind, record: Record, args) -> str:
        old = self._pick_value(record, kind, args, 0)
        new = self._arg(args, 1, f"New {kind.singular}: ")
        if not getattr(record, kind.edit)(old.value, new):
            raise ValueError(f"{kind.title} {new} already exists for {record.name}.")
        return f"{kind.title} updated."

    def _remove_value(self, kind: ValueKind, record: Record, args) -> str:
        old = self._pick_value(record, kind, args, 0)
        getattr(record, kind.remove)(old.value)
        return f"{kind.title} removed."

    def hello(self, args) -> str:
        return f"How can I help you?\n{HELP_TEXT}"

    @input_error
    def add_contact(self, args) -> str:
        name = self._arg(args, 0, "Contact name: ")
        if len(args) > 1:
            phone = args[1].strip()
        elif not args:
            phone = ask("Phone (empty to skip): ")
        else:
            phone = ""
        record = Record(name)
        # Add the phone before touching the book, so an invalid phone changes nothing
        if phone:
            record.add_phone(phone)
        existing = self.book.find_by_name(name, exact=True)
        if existing:
            if phone:
                action = choose([ADD_TO_EXISTING, CREATE_NEW], header=f"Contact '{name}' already exists:")
                if action == ADD_TO_EXISTING:
                    target = choose(existing, header=f"Several contacts are named '{name}':")
                    if not target.add_phone(phone):
                        return f"Phone already exists for {target.name}."
                    return "Contact updated."
            elif not confirm(f"Contact '{name}' already exists. Create another one?"):
                raise Cancelled
        self.book.add_record(record)
        return "Contact added."

    @input_error
    def add_phone(self, args) -> str:
        return self._add_value(PHONE, self._select_record(args), args[1:])

    @input_error
    def add_email(self, args) -> str:
        return self._add_value(EMAIL, self._select_record(args), args[1:])

    @input_error
    def add_address(self, args) -> str:
        return self._add_value(ADDRESS, self._select_record(args), args[1:])

    @input_error
    def change_phone(self, args) -> str:
        return self._change_value(PHONE, self._select_record(args), args[1:])

    @input_error
    def change_email(self, args) -> str:
        return self._change_value(EMAIL, self._select_record(args), args[1:])

    @input_error
    def change_address(self, args) -> str:
        return self._change_value(ADDRESS, self._select_record(args), args[1:])

    @input_error
    def remove_phone(self, args) -> str:
        return self._remove_value(PHONE, self._select_record(args), args[1:])

    @input_error
    def remove_email(self, args) -> str:
        return self._remove_value(EMAIL, self._select_record(args), args[1:])

    @input_error
    def remove_address(self, args) -> str:
        return self._remove_value(ADDRESS, self._select_record(args), args[1:])

    @input_error
    def change_name(self, args) -> str:
        record = self._select_record(args)
        record.edit_name(self._arg(args, 1, "New name: "))
        return "Name updated."

    @input_error
    def edit_contact(self, args) -> str:
        record = self._select_record(args)
        field = choose(CONTACT_FIELDS, header=f"Which field of {record.name} to edit?")
        if field == "Name":
            record.edit_name(self._arg([], 0, "New name: "))
            return "Name updated."
        if field == "Birthday":
            replaced = record.add_birthday(self._arg([], 0, "Birthday (DD.MM.YYYY): "))
            return "Birthday updated." if replaced else "Birthday added."
        kind = {"Phone": PHONE, "Email": EMAIL, "Address": ADDRESS}[field]
        return self._change_value(kind, record, [])

    @input_error
    def delete_contact(self, args) -> str:
        record = self._select_record(args)
        if not confirm(f'Delete "{record.name}"?'):
            raise Cancelled
        self.book.delete(record)
        return "Contact deleted."

    @input_error
    def show_phone(self, args) -> str:
        record = self._select_record(args)
        return "; ".join(p.value for p in record.phones) or "No phones."

    @input_error
    def search_contacts(self, args) -> str:
        text = self._text_arg(args, "Search text: ")
        found = self.book.search(text)
        return numbered(found) if found else "No contacts found."

    @input_error
    def show_all(self, args) -> str:
        if not self.book:
            return "No contacts."
        return "\n".join(str(record) for record in self.book)

    @input_error
    def add_birthday(self, args) -> str:
        record = self._select_record(args)
        replaced = record.add_birthday(self._arg(args, 1, "Birthday (DD.MM.YYYY): "))
        return "Birthday updated." if replaced else "Birthday added."

    @input_error
    def show_birthday(self, args) -> str:
        record = self._select_record(args)
        if record.birthday is None:
            return f"Birthday is not set for {record.name}."
        return str(record.birthday)

    @input_error
    def birthdays(self, args) -> str:
        days = Birthday.UPCOMING_DAYS
        if args:
            if not (args[0].isascii() and args[0].isdigit()) or int(args[0]) < 1:
                raise ValueError("Days must be a positive integer.")
            days = int(args[0])
        upcoming = self.book.get_upcoming_birthdays(days)
        if not upcoming:
            return f"No birthdays in the next {days} days."
        lines = []
        for item in upcoming:
            line = (
                f"Congratulate {item.record.name} on "
                f"{item.congratulation_date:%d.%m.%Y} ({item.congratulation_date:%a})"
            )
            if item.birthday_date != item.congratulation_date:
                line += f", birthday on {item.birthday_date:%d.%m.%Y} ({item.birthday_date:%a})"
            lines.append(line)
        return "\n".join(lines)

    @input_error
    def add_note(self, args) -> str:
        title = self._arg(args, 0, "Title: ")
        text = self._arg(args, 1, "Text: ")
        tags = args[2:] if len(args) >= 2 else ask("Tags (space separated, empty to skip): ").split()
        self.notes.add_note(Note(title, text, tags))
        return "Note added."

    @input_error
    def show_notes(self, args) -> str:
        if not self.notes:
            return "No notes."
        return numbered(self.notes)

    @input_error
    def search_notes(self, args) -> str:
        found = self.notes.search(self._text_arg(args, "Search text: "))
        return numbered(found) if found else "No notes found."

    @input_error
    def search_notes_by_tag(self, args) -> str:
        tag = self._arg(args, 0, "Tag: ")
        found = self.notes.find_by_tag(tag)
        return numbered(found) if found else "No notes found."

    @input_error
    def sort_notes_by_tags(self, args) -> str:
        groups = {f"#{tag}": notes for tag, notes in self.notes.group_by_tag().items()}
        untagged = self.notes.untagged()
        if untagged:
            groups["(no tags)"] = untagged
        if not groups:
            return "No notes."
        return "\n".join(
            f"{header}\n" + "\n".join(f"  {note}" for note in notes) for header, notes in groups.items()
        )

    @input_error
    def edit_note(self, args) -> str:
        note = self._select_note(args)
        field = choose(NOTE_FIELDS, header=f'Which part of "{note.title}" to edit?')
        if field == "Title":
            note.edit_title(self._arg([], 0, "New title: "))
            return "Title updated."
        note.edit_text(self._arg([], 0, "New text: "))
        return "Text updated."

    @input_error
    def add_tag(self, args) -> str:
        note = self._select_note(args[:1])
        tags = args[1:] or ask("Tags (space separated): ").split()
        if not tags:
            raise ValueError("The value cannot be empty.")
        added = [tag for tag in tags if note.add_tag(tag)]
        return "Tags added." if added else "Note already has these tags."

    @input_error
    def remove_tag(self, args) -> str:
        note = self._select_note(args[:1])
        if len(args) > 1:
            tag = args[1]
        else:
            if not note.tags:
                raise ValueError("The note has no tags.")
            tag = choose(note.tags, header="Choose the tag:").value
        if not note.remove_tag(tag):
            raise ValueError(f"Tag {tag} not found in the note.")
        return "Tag removed."

    @input_error
    def delete_note(self, args) -> str:
        note = self._select_note(args)
        if not confirm(f'Delete "{note.title}"?'):
            raise Cancelled
        self.notes.delete(note)
        return "Note deleted."

    def run(self) -> None:
        """Read commands from the console until the user quits."""
        print("Welcome to the assistant bot!")
        self.completer.install()
        while True:
            try:
                with self.completer.active():
                    user_input = input("Enter a command: ")
                command, args = parse_input(user_input)
            except (EOFError, KeyboardInterrupt):
                print("\nGood bye!")
                break
            except ValueError:
                print("Invalid input: a double quote is not closed.")
                continue

            if command in ["close", "exit"]:
                print("Good bye!")
                break

            handler = self.commands.get(command)
            if handler is None:
                print("Unknown command.")
                print(HELP_TEXT)
                continue
            try:
                print(handler(args))
            except (EOFError, KeyboardInterrupt):
                print("\nGood bye!")
                break
