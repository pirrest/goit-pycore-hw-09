from address_book import AddressBook
from bot.bot import Bot


def main():
    book = AddressBook.load()
    try:
        Bot(book).run()
    finally:
        book.save()


if __name__ == "__main__":
    main()
