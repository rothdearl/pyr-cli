import os
import unittest
from typing import final

from pyrcli.cli import ini


@final
class TestINI(unittest.TestCase):
    """Tests the ini module."""

    def test_read(self) -> None:
        # File does not exist.
        self.assertFalse(ini.load_config("", clear_previous=False, on_error=print))

        # File is invalid.
        self.assertFalse(
            ini.load_config(os.path.join("test_data", "invalid-ini-file.ini"), clear_previous=False, on_error=print))

        # No options.
        self.assertTrue(ini.is_empty())
        self.assertFalse(ini.has_defaults())
        self.assertFalse(ini.has_sections())

        # Valid file with options.
        self.assertTrue(
            ini.load_config(os.path.join("test_data", "valid-ini-file.ini"), clear_previous=True, on_error=print))

        # Has options.
        self.assertFalse(ini.is_empty())
        self.assertTrue(ini.has_defaults())
        self.assertTrue(ini.has_sections())

    def test_values_bool(self) -> None:
        # Truthy.
        self.assertTrue(ini.get_bool_option("bool_options", "truthy_1"))
        self.assertTrue(ini.get_bool_option("bool_options", "truthy_on"))
        self.assertTrue(ini.get_bool_option("bool_options", "truthy_true"))
        self.assertTrue(ini.get_bool_option("bool_options", "truthy_y"))
        self.assertTrue(ini.get_bool_option("bool_options", "truthy_yes"))

        # Falsy.
        self.assertFalse(ini.get_bool_option("bool_options", "falsy_0"))
        self.assertFalse(ini.get_bool_option("bool_options", "falsy_false"))
        self.assertFalse(ini.get_bool_option("bool_options", "falsy_off"))
        self.assertFalse(ini.get_bool_option("bool_options", "falsy_n"))
        self.assertFalse(ini.get_bool_option("bool_options", "falsy_no"))

        # Fallback.
        self.assertFalse(ini.get_bool_option("bool_options", "empty_value"))
        self.assertFalse(ini.get_bool_option("bool_options", "missing_value"))
        self.assertFalse(ini.get_bool_option("missing_section", "truthy_1"))

        # Invalid.
        self.assertIsNone(ini.get_bool_option("bool_options", "invalid_value"))

    def test_values_dict(self) -> None:
        section = "dict_options"

        # Valid.
        self.assertEqual(ini.get_dict_option(section, "valid_dict"), {"a": 1, "b": True})
        self.assertIsInstance(ini.get_dict_option(section, "valid_dict"), dict)
        self.assertEqual(ini.get_dict_option(section, "valid_dicts"),
                         {"a": 1, "b": True, "c": {"d": 15.0, "e": "true"}})
        self.assertIsInstance(ini.get_dict_option(section, "valid_dicts"), dict)

        # Invalid.
        self.assertIsNone(ini.get_dict_option(section, "invalid_array"))
        self.assertIsNone(ini.get_dict_option(section, "invalid_string"))
        self.assertIsNone(ini.get_dict_option(section, "invalid_number"))
        self.assertIsNone(ini.get_dict_option(section, "invalid_bool"))
        self.assertIsNone(ini.get_dict_option(section, "valid_null"))

        # Fallback.
        self.assertEqual(ini.get_dict_option(section, "empty_value"), {})
        self.assertEqual(ini.get_dict_option(section, "missing_value"), {})
        self.assertEqual(ini.get_dict_option("missing_section", "valid_object"), {})

        # Invalid.
        self.assertIsNone(ini.get_dict_option(section, "invalid_value"))

    def test_values_float(self) -> None:
        # Valid.
        self.assertEqual(ini.get_float_option("float_options", "valid_float"), 3.14159)
        self.assertEqual(ini.get_float_option("float_options", "valid_int_like"), 10.0)
        self.assertEqual(ini.get_float_option("float_options", "negative_float"), -2.5)
        self.assertEqual(ini.get_float_option("float_options", "scientific"), 1000.0)

        # Fallback.
        self.assertEqual(ini.get_float_option("float_options", "empty_value"), 0.0)
        self.assertEqual(ini.get_float_option("float_options", "missing_value"), 0.0)
        self.assertEqual(ini.get_float_option("missing_section", "valid_float"), 0.0)

        # Invalid.
        self.assertIsNone(ini.get_float_option("float_options", "invalid_value"))

    def test_values_int(self) -> None:
        # Valid.
        self.assertEqual(ini.get_int_option("int_options", "valid_int"), 42)
        self.assertEqual(ini.get_int_option("int_options", "negative_int"), -7)
        self.assertEqual(ini.get_int_option("int_options", "zero"), 0)

        # Fallback.
        self.assertEqual(ini.get_int_option("int_options", "empty_value"), 0.0)
        self.assertEqual(ini.get_int_option("int_options", "missing_value"), 0.0)
        self.assertEqual(ini.get_int_option("missing_section", "valid_int"), 0.0)

        # Invalid.
        self.assertIsNone(ini.get_int_option("int_options", "invalid_value"))
        self.assertIsNone(ini.get_int_option("int_options", "invalid_string"))

    def test_values_string(self) -> None:
        # Valid.
        self.assertEqual(ini.get_str_option("string_options", "normal_string"), "hello world")

        # Fallback.
        self.assertEqual(ini.get_str_option("string_options", "empty_value"), "")
        self.assertEqual(ini.get_str_option("string_options", "missing_value"), "")
        self.assertEqual(ini.get_str_option("missing_section", "normal_string"), "")

    def test_values_strings(self) -> None:
        section = "string_list_option"

        # Valid.
        self.assertEqual(ini.get_str_list_option(section, "comma_separated"), ["a", "b", "c"])
        self.assertEqual(ini.get_str_list_option(section, "tab_separated", separator="\t"), ["a", "b", "c", "d"])
        self.assertEqual(ini.get_str_list_option(section, "comma_with_spaces"), ["a", "b", "c"])
        self.assertEqual(ini.get_str_list_option(section, "leading_trailing"), ["a", "b"])
        self.assertEqual(ini.get_str_list_option(section, "only_separators"), [])
        self.assertEqual(ini.get_str_list_option(section, "single_value"), ["one"])

        # Fallback.
        self.assertEqual(ini.get_str_list_option(section, "empty_value"), [])
        self.assertEqual(ini.get_str_list_option(section, "missing_value"), [])
        self.assertEqual(ini.get_str_list_option("missing_section", "comma_separated"), [])
