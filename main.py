from address_book import AddressBook
from bot.bot import Bot
from notes import NoteBook


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
