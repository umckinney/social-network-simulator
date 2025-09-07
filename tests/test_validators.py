# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring

import unittest
from unittest.mock import patch
import social_network.validators as local_validators


class TestValidators(unittest.TestCase):
    def test_attribute_length_validator_valid(self):
        self.assertTrue(local_validators.attribute_length_validator("abc", "user_id"))

    def test_attribute_length_validator_invalid(self):
        self.assertFalse(
            local_validators.attribute_length_validator("a" * 33, "user_id")
        )

    def test_attribute_length_validator_unknown_attribute(self):
        self.assertFalse(
            local_validators.attribute_length_validator("abc", "unknown_attr")
        )

    @patch("os.path.isfile", return_value=True)
    def test_file_name_validator_valid(self, _mock_isfile):
        with patch("os.path.basename", return_value="valid_file.csv"):
            self.assertTrue(local_validators.file_name_validator("valid_file.csv"))

    @patch("os.path.isfile", return_value=False)
    def test_file_name_validator_file_not_exist(self, _mock_isfile):
        self.assertFalse(local_validators.file_name_validator("missing_file.csv"))

    @patch("os.path.isfile", return_value=True)
    def test_csv_extension_validator_invalid_extension(self, _mock_isfile):
        with patch("os.path.basename", return_value="badfile.txt"):
            self.assertFalse(local_validators.csv_extension_validator("badfile.txt"))

    @patch("os.path.isfile", return_value=True)
    def test_file_name_validator_invalid_chars(self, _mock_isfile):
        with patch("os.path.basename", return_value="bad|name.csv"):
            self.assertFalse(local_validators.file_name_validator("bad|name.csv"))

    def test_string_validator_valid(self):
        self.assertTrue(local_validators.string_validator("Hello"))

    def test_string_validator_invalid_empty(self):
        self.assertFalse(local_validators.string_validator(""))

    def test_string_validator_invalid_whitespace(self):
        self.assertFalse(local_validators.string_validator("   "))

    def test_string_validator_invalid_type(self):
        self.assertFalse(local_validators.string_validator(123))

    def test_user_email_validator_valid(self):
        self.assertTrue(local_validators.user_email_validator("test@example.com"))

    def test_user_email_validator_invalid_format(self):
        self.assertFalse(local_validators.user_email_validator("bad-email"))

    def test_user_email_validator_invalid_type(self):
        self.assertFalse(local_validators.user_email_validator(1234))
