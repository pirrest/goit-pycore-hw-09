import unittest
from unittest.mock import patch

from bot.prompt import Cancelled, choose, confirm


class ChooseTest(unittest.TestCase):
    def test_single_item_is_returned_without_asking(self):
        with patch("builtins.input", side_effect=AssertionError):
            self.assertEqual(choose(["only"]), "only")

    def test_empty_list_is_an_error(self):
        with self.assertRaises(ValueError):
            choose([])

    def test_picks_by_number_and_repeats_on_bad_input(self):
        with patch("builtins.input", side_effect=["x", "0", "3", "2"]), patch("builtins.print") as printed:
            self.assertEqual(choose(["a", "b"]), "b")
        output = "\n".join(str(call.args[0]) for call in printed.call_args_list)
        self.assertIn("1. a", output)
        self.assertIn("2. b", output)
        self.assertIn("Enter a number from 1 to 2.", output)

    def test_empty_answer_cancels(self):
        with patch("builtins.input", return_value=""), patch("builtins.print"):
            with self.assertRaises(Cancelled):
                choose(["a", "b"])


class ConfirmTest(unittest.TestCase):
    def test_confirm(self):
        for answer, expected in [("y", True), ("YES", True), ("n", False), ("", False), ("maybe", False)]:
            with self.subTest(answer=answer):
                with patch("builtins.input", return_value=answer):
                    self.assertEqual(confirm("Sure?"), expected)


if __name__ == "__main__":
    unittest.main()
