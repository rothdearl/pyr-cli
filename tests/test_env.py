import os
import unittest
from typing import final
from unittest.mock import patch

from pyrcli.cli import env

_KEY = "_PYR_CLI_TEST_VAR"


@final
class TestEnv(unittest.TestCase):
    """Test the env module."""

    def test_get_env_str(self) -> None:
        """Test the get_env_str function."""
        # 1) Returns the value when the variable is set.
        with patch.dict(os.environ, {_KEY: "hello"}):
            self.assertEqual(env.get_env_str(_KEY), "hello")

        # 2) Returns None when the variable is unset.
        with patch.dict(os.environ):
            os.environ.pop(_KEY, None)
            self.assertIsNone(env.get_env_str(_KEY))

        # 3) Returns a custom default when the variable is unset.
        with patch.dict(os.environ):
            os.environ.pop(_KEY, None)
            self.assertEqual(env.get_env_str(_KEY, "fallback"), "fallback")

        # 4) Trims surrounding whitespace when trim=True (default).
        with patch.dict(os.environ, {_KEY: "  hello  "}):
            self.assertEqual(env.get_env_str(_KEY), "hello")

        # 5) Does not trim when trim=False.
        with patch.dict(os.environ, {_KEY: "  hello  "}):
            self.assertEqual(env.get_env_str(_KEY, trim=False), "  hello  ")

        # 6) Returns default for a whitespace-only value when trim=True.
        with patch.dict(os.environ, {_KEY: "   "}):
            self.assertIsNone(env.get_env_str(_KEY))

        # 7) Returns a whitespace-only value unchanged when trim=False.
        with patch.dict(os.environ, {_KEY: "   "}):
            self.assertEqual(env.get_env_str(_KEY, trim=False), "   ")

        # 8) Returns default for an empty string value.
        with patch.dict(os.environ, {_KEY: ""}):
            self.assertIsNone(env.get_env_str(_KEY))

    def test_get_required_env_str(self) -> None:
        """Test the get_required_env_str function."""
        errors = []

        # 1) Returns the value when the variable is set.
        with patch.dict(os.environ, {_KEY: "hello"}):
            self.assertEqual(env.get_required_env_str(_KEY, on_error=errors.append), "hello")
            self.assertEqual(errors, [])

        # 2) Returns None and calls on_error when the variable is unset.
        with patch.dict(os.environ):
            os.environ.pop(_KEY, None)
            result = env.get_required_env_str(_KEY, on_error=errors.append)
            self.assertIsNone(result)
            self.assertEqual(len(errors), 1)
            self.assertIn(_KEY, errors[0])
            errors.clear()

        # 3) Returns None and calls on_error for a whitespace-only value when trim=True.
        with patch.dict(os.environ, {_KEY: "   "}):
            result = env.get_required_env_str(_KEY, on_error=errors.append)
            self.assertIsNone(result)
            self.assertEqual(len(errors), 1)
            errors.clear()

        # 4) Trims surrounding whitespace when trim=True (default).
        with patch.dict(os.environ, {_KEY: "  hello  "}):
            self.assertEqual(env.get_required_env_str(_KEY, on_error=errors.append), "hello")
            self.assertEqual(errors, [])

        # 5) Returns the untrimmed value when trim=False.
        with patch.dict(os.environ, {_KEY: "  hello  "}):
            self.assertEqual(env.get_required_env_str(_KEY, trim=False, on_error=errors.append), "  hello  ")
            self.assertEqual(errors, [])
