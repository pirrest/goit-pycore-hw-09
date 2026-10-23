from typing import Sequence, TypeVar

T = TypeVar("T")


class Cancelled(Exception):
    """Raised when the user cancels an interactive step."""


def ask(prompt: str) -> str:
    """Read a stripped line from the console."""
    return input(prompt).strip()


def choose(items: Sequence[T], header: str = "Found several matches:") -> T:
    """Return the only item, or let the user pick one from a numbered list.

    Raises:
        ValueError: If there is nothing to choose from.
        Cancelled: If the user enters an empty line.
    """
    if not items:
        raise ValueError("Nothing to choose from.")
    if len(items) == 1:
        return items[0]
    print(header)
    for number, item in enumerate(items, start=1):
        print(f"  {number}. {item}")
    while True:
        answer = ask("Enter the number (empty to cancel): ")
        if not answer:
            raise Cancelled
        if answer.isascii() and answer.isdigit() and 1 <= int(answer) <= len(items):
            return items[int(answer) - 1]
        print(f"Enter a number from 1 to {len(items)}.")


def confirm(question: str) -> bool:
    """Ask a yes/no question and return True for 'y' or 'yes'."""
    return ask(f"{question} (y/n): ").casefold() in ("y", "yes")
