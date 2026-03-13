import unittest
from typing import final

from pyrcli.cli import terminal


@final
class TestTerminal(unittest.TestCase):
    """Test the terminal module."""

    def test_terminal_predicates(self) -> None:
        self.assertFalse(terminal.stderr_is_redirected())
        self.assertTrue(terminal.stderr_is_terminal())
        self.assertFalse(terminal.stdin_is_redirected())
        self.assertTrue(terminal.stdin_is_terminal())
        self.assertFalse(terminal.stdout_is_redirected())
        self.assertTrue(terminal.stdout_is_terminal())
