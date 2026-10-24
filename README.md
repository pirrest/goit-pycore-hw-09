# Personal Assistant

A command-line personal assistant that keeps your **contacts** and **notes**
on disk, so nothing is lost between runs.

- Contacts with a name, phones, emails, addresses and a birthday, validated on input.
- Search over every field of a contact, edit and delete contacts.
- Upcoming birthdays within a chosen number of days.
- Text notes with tags, search by text or tag, notes grouped by tag.
- Tab completion of command names.
- No third-party dependencies, Python 3.10 or newer.

## Installation

### For users

[pipx](https://pipx.pypa.io/) installs the `assistant` command in an isolated
environment, so it is available from any directory:

```bash
pipx install git+https://github.com/pirrest/goit-pycore-hw-09
```

Or from a clone of the repository:

```bash
git clone https://github.com/pirrest/goit-pycore-hw-09
cd goit-pycore-hw-09
pipx install .
```

Without pipx, install into a virtual environment (the command is available
while the environment is active):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install .
```

### For development

```bash
git clone https://github.com/pirrest/goit-pycore-hw-09
cd goit-pycore-hw-09
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

An editable install picks up code changes without reinstalling.

## Running

```bash
assistant
```

or

```bash
python -m personal_assistant
```

Type `help` to see all commands, `exit` or `close` to quit.

### Where the data is stored

Data lives in the `.personal_assistant` folder of your home directory and is
saved when you quit:

| File                              | Content  |
|-----------------------------------|----------|
| `~/.personal_assistant/contacts.pkl` | contacts |
| `~/.personal_assistant/notes.pkl`    | notes    |

A file that cannot be read is renamed to `*.bak` and the assistant starts with
empty data, so the broken file is never overwritten.

## Usage

### How commands work

- Arguments are separated by spaces. **Put a value with spaces in double
  quotes**: `add-address Alice "Kyiv, Khreshchatyk 1"`.
- **Missing arguments are asked for**: type `add-email` alone and the assistant
  asks for the name and the email.
- Press **Tab** to complete a command name; press it twice to list the options.
- When a name or a search matches **several records**, they are shown as a
  numbered list and you choose one by its number. An empty line cancels.

### Commands

Contacts:

| Command                                          | Description                                              |
|--------------------------------------------------|----------------------------------------------------------|
| `add [name] [phone]`                             | add a contact, or a phone to an existing one             |
| `add-phone [name] [phone]`                       | add a phone to a contact                                 |
| `add-email [name] [email]`                       | add an email to a contact                                |
| `add-address [name] [address]`                   | add an address to a contact                              |
| `add-birthday [name] [DD.MM.YYYY]`               | set a contact's birthday                                 |
| `change [name] [old phone] [new phone]`          | change a phone (alias: `change-phone`)                   |
| `change-email [name] [old] [new]`                | change an email                                          |
| `change-address [name] [old] [new]`              | change an address                                        |
| `change-name [name] [new name]`                  | rename a contact                                         |
| `remove-phone`, `remove-email`, `remove-address` `[name] [value]` | remove a phone, an email or an address |
| `edit-contact [name]`                            | choose a field and edit it                               |
| `delete-contact [name]`                          | delete a contact (asks for confirmation)                 |
| `phone [name]`                                   | show a contact's phones                                  |
| `show-birthday [name]`                           | show a contact's birthday                                |
| `search [text]`                                  | find contacts by any field                               |
| `all`, `list`, `contacts`                        | show all contacts                                        |
| `birthdays [days]`                               | birthdays in the next days (7 by default)                |

Notes:

| Command                                 | Description                                  |
|-----------------------------------------|----------------------------------------------|
| `add-note [title] [text] [tags...]`     | add a note                                   |
| `all-notes`, `notes`                    | show all notes                               |
| `search-notes [text]`                   | find notes by title or text                  |
| `search-notes-tag [tag]`                | find notes with a tag                        |
| `sort-notes-tags`                       | show notes grouped by tag                    |
| `edit-note [text]`                      | edit the title or the text of a note         |
| `add-tag [note] [tags...]`              | add tags to a note                           |
| `remove-tag [note] [tag]`               | remove a tag from a note                     |
| `delete-note [note]`                    | delete a note (asks for confirmation)        |

Other: `hello` or `help` shows the command list, `exit` or `close` quits.

### Input rules

- **Phone**: spaces, hyphens, dots and parentheses are allowed. `0501234567`,
  `050-123-45-67` and `+38 (050) 123-45-67` are all stored as `+380501234567`.
  A number with another country code needs a leading `+`, for example
  `+48 600 700 800` (10 to 15 digits).
- **Email**: `name@domain.com`.
- **Birthday**: `DD.MM.YYYY`, for example `05.03.1990`.
- **Tag**: a single word, with or without `#`, stored in lowercase.
- Several contacts may share a name. Contacts may have several phones, emails
  and addresses.
- Contacts are picked by name (a part of the name is enough). Notes are picked
  by a part of the title or the text.

### Example: contacts

Several contacts with the same name, and choosing between them:

```text
Enter a command: add Alice 050-123-45-67
Contact added.
Enter a command: add-email Alice alice@example.com
Email added.
Enter a command: add-address Alice "Kyiv, Khreshchatyk 1"
Address added.
Enter a command: add-birthday Alice 25.10.1990
Birthday added.
Enter a command: add Alice 0991112233
Contact 'Alice' already exists:
  1. Add the phone to the existing contact
  2. Create a new contact
Enter the number (empty to cancel): 1
Contact updated.
Enter a command: add Alice 0671234567
Contact 'Alice' already exists:
  1. Add the phone to the existing contact
  2. Create a new contact
Enter the number (empty to cancel): 2
Contact added.
Enter a command: all
Contact name: Alice, phones: +380501234567; +380991112233, emails: alice@example.com, addresses: Kyiv, Khreshchatyk 1, birthday: 25.10.1990
Contact name: Alice, phones: +380671234567, emails: , addresses: , birthday: -
```

A command that needs one contact asks which one when several match, and
validates the input:

```text
Enter a command: add-email Alice not-an-email
Several contacts match 'Alice':
  1. Contact name: Alice, phones: +380501234567; +380991112233, emails: alice@example.com, addresses: Kyiv, Khreshchatyk 1, birthday: 25.10.1990
  2. Contact name: Alice, phones: +380671234567, emails: , addresses: , birthday: -
Enter the number (empty to cancel): 1
Invalid email. Use name@domain.com
```

Search looks through every field, phones are matched by digits:

```text
Enter a command: search kyiv
1. Contact name: Alice, phones: +380501234567; +380991112233, emails: alice@example.com, addresses: Kyiv, Khreshchatyk 1, birthday: 25.10.1990
Enter a command: search 067
1. Contact name: Alice, phones: +380671234567, emails: , addresses: , birthday: -
```

Missing arguments are asked for step by step:

```text
Enter a command: change-phone Alice
Several contacts match 'Alice':
  1. Contact name: Alice, phones: +380501234567; +380991112233, emails: alice@example.com, addresses: Kyiv, Khreshchatyk 1, birthday: 25.10.1990
  2. Contact name: Alice, phones: +380671234567, emails: , addresses: , birthday: -
Enter the number (empty to cancel): 1
Choose the phone:
  1. +380501234567
  2. +380991112233
Enter the number (empty to cancel): 1
New phone: 0931234567
Phone updated.
```

### Example: upcoming birthdays

`birthdays [days]` lists birthdays from today up to the given number of days.
A birthday that falls on a weekend is congratulated on the next Monday, and the
real date is shown too. Here, today is Friday, 23.10.2026, Bob's birthday is
24.10 and Carl's is 27.10:

```text
Enter a command: birthdays
Congratulate Bob on 26.10.2026 (Mon), birthday on 24.10.2026 (Sat)
Congratulate Carl on 27.10.2026 (Tue)
Enter a command: birthdays 2
Congratulate Bob on 26.10.2026 (Mon), birthday on 24.10.2026 (Sat)
```

### Example: notes and tags

Dates in parentheses are the creation time of a note, shortened to `(date)`
below.

```text
Enter a command: add-note Milk "Buy 2 liters of milk" shop home
Note added.
Enter a command: add-note Gift "Buy a birthday gift" shop
Note added.
Enter a command: add-note Idea "Write the report"
Note added.
Enter a command: search-notes buy
1. Milk: Buy 2 liters of milk [#shop #home] (date)
2. Gift: Buy a birthday gift [#shop] (date)
Enter a command: search-notes-tag home
1. Milk: Buy 2 liters of milk [#shop #home] (date)
Enter a command: sort-notes-tags
#home
  Milk: Buy 2 liters of milk [#shop #home] (date)
#shop
  Milk: Buy 2 liters of milk [#shop #home] (date)
  Gift: Buy a birthday gift [#shop] (date)
(no tags)
  Idea: Write the report (date)
Enter a command: add-tag idea work
Tags added.
Enter a command: delete-note gift
Delete "Gift"? (y/n): y
Note deleted.
```

`sort-notes-tags` groups notes by tag in alphabetical order. A note with
several tags is listed under each of them, notes without tags come last.

## Development

Install in editable mode (see above), then run the tests:

```bash
python -m unittest
```

The source lives in `src/personal_assistant`:

| Package         | Content                                                        |
|-----------------|----------------------------------------------------------------|
| `address_book`  | `AddressBook`, `Record` and the contact fields                 |
| `notes`         | `NoteBook`, `Note` and the note fields                         |
| `storage`       | `FileStorage` that saves and loads data with pickle            |
| `common`        | base classes of the fields shared by contacts and notes        |
| `bot`           | the command handlers, interactive prompts and Tab completion   |

### Debugging

`src/` is not on the import path by itself, so install the package with
`pip install -e .` first. Then run the module `personal_assistant`:

- **PyCharm**: Run Configuration of the type "Python", switch the script path
  to "Module name" and enter `personal_assistant`. Mark `src` as Sources Root.
- **VS Code**: a `launch.json` configuration with `"module": "personal_assistant"`
  and `"console": "integratedTerminal"`.

## License

[MIT](LICENSE)
