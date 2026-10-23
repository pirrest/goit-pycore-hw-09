from contextlib import contextmanager
from typing import Iterable, Iterator

try:
    import readline
except ImportError:  # no readline on this platform, completion is simply unavailable
    readline = None


class CommandCompleter:
    """Completes the command name with the Tab key in the console prompt.

    Completion is active only inside `active()`, so answers to the interactive
    questions of the commands are not completed.
    """

    def __init__(self, commands: Iterable[str]):
        self.commands = sorted(commands)
        self.enabled = False
        self._matches: list[str] = []

    def install(self) -> None:
        """Register the completer in readline; does nothing if readline is unavailable."""
        if readline is None:
            return
        readline.set_completer_delims(" \t\n")
        readline.set_completer(self.complete)
        # macOS Python is often linked against libedit, which uses another binding syntax
        if "libedit" in (readline.__doc__ or ""):
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

    @contextmanager
    def active(self) -> Iterator[None]:
        """Enable completion while the command prompt is waiting for input."""
        self.enabled = True
        try:
            yield
        finally:
            self.enabled = False

    def complete(self, text: str, state: int) -> str | None:
        """Return the state-th command starting with the text, as readline expects."""
        if not self.enabled or readline is None:
            return None
        if state == 0:
            before_word = readline.get_line_buffer()[:readline.get_begidx()]
            if before_word.strip():
                # Only the first word of the line is a command
                self._matches = []
            else:
                self._matches = [command for command in self.commands if command.startswith(text.lower())]
        return self._matches[state] if state < len(self._matches) else None
