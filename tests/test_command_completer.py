import unittest
from unittest.mock import patch

from personal_assistant.bot.command_completer import CommandCompleter


class CommandCompleterTest(unittest.TestCase):
    def setUp(self):
        self.completer = CommandCompleter(["add", "add-note", "all", "exit"])

    def complete_all(self, text, line=None, begidx=0):
        line = text if line is None else line
        with patch("personal_assistant.bot.command_completer.readline") as readline:
            readline.get_line_buffer.return_value = line
            readline.get_begidx.return_value = begidx
            results = []
            while (match := self.completer.complete(text, len(results))) is not None:
                results.append(match)
        return results

    def test_completes_command_prefix(self):
        with self.completer.active():
            self.assertEqual(self.complete_all("a"), ["add", "add-note", "all"])
            self.assertEqual(self.complete_all("add-"), ["add-note"])
            self.assertEqual(self.complete_all("AD"), ["add", "add-note"])
            self.assertEqual(self.complete_all("zzz"), [])

    def test_does_not_complete_arguments(self):
        with self.completer.active():
            self.assertEqual(self.complete_all("a", line="add a", begidx=4), [])

    def test_inactive_outside_of_command_prompt(self):
        self.assertEqual(self.complete_all("a"), [])
        with self.completer.active():
            pass
        self.assertEqual(self.complete_all("a"), [])


if __name__ == "__main__":
    unittest.main()
