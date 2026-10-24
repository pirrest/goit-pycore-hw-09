from personal_assistant.address_book import AddressBook
from personal_assistant.bot.bot import Bot
from personal_assistant.notes import NoteBook


def main():
    book = AddressBook.load()
    notes = NoteBook.load()
    try:
        Bot(book, notes).run()
    finally:
        book.save()
        notes.save()


if __name__ == "__main__":
    main()
