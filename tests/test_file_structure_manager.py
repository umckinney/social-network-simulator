# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring

import unittest
from unittest.mock import patch
from pathlib import Path
import social_network.file_structure_manager as file_structure_manager


class TestFileStructureManager(unittest.TestCase):

    def setUp(self):
        self.valid_record = {
            "id": 1,
            "user_id": "user01",
            "picture_id": "pic123",
            "tags": ["tag1", "tag2"],
        }

    @patch("social_network.file_structure_manager.safe_parse_tags")
    def test_get_path_success(self, mock_parse_tags):
        mock_parse_tags.return_value = self.valid_record
        path = file_structure_manager.get_path(self.valid_record)
        expected = Path("picture_storage") / "user01" / "tag1" / "tag2"
        self.assertEqual(path, expected)

    @patch("social_network.file_structure_manager.safe_parse_tags")
    def test_get_path_missing_tags(self, mock_parse_tags):
        record = self.valid_record.copy()
        record["tags"] = []
        mock_parse_tags.return_value = record
        path = file_structure_manager.get_path(record)
        self.assertEqual(path, Path("picture_storage") / "user01")

    def test_get_path_key_error(self):
        broken_record = {"tags": ["a", "b"]}
        path = file_structure_manager.get_path(broken_record)
        self.assertIsNone(path)

    @patch("social_network.file_structure_manager.get_path")
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text")
    def test_create_pointer_file_success(self, mock_write, _mock_mkdir, mock_get_path):
        mock_path = Path("/fake/path")
        mock_get_path.return_value = mock_path
        mock_write.return_value = None
        record = self.valid_record.copy()
        record["tags"] = ["x", "y"]
        result = file_structure_manager.create_pointer_file(record)
        self.assertTrue(result)
        mock_write.assert_called_once()

    def test_create_pointer_file_invalid_id(self):
        record = self.valid_record.copy()
        record["id"] = "abc"
        result = file_structure_manager.create_pointer_file(record)
        self.assertFalse(result)

    def test_create_pointer_file_missing_id(self):
        record = self.valid_record.copy()
        del record["id"]
        result = file_structure_manager.create_pointer_file(record)
        self.assertFalse(result)

    @patch("social_network.file_structure_manager.get_path", return_value=Path("/cannot/write"))
    @patch("pathlib.Path.mkdir", side_effect=PermissionError)
    def test_create_pointer_file_permission_error_on_mkdir(
        self, _mock_mkdir, _mock_get_path
    ):
        record = self.valid_record.copy()
        result = file_structure_manager.create_pointer_file(record)
        self.assertFalse(result)

    @patch("social_network.file_structure_manager.get_path", return_value=Path("/cannot/write"))
    @patch("pathlib.Path.mkdir", side_effect=OSError("Disk error"))
    def test_create_pointer_file_oserror_on_mkdir(self, _mock_mkdir, _mock_get_path):
        record = self.valid_record.copy()
        result = file_structure_manager.create_pointer_file(record)
        self.assertFalse(result)

    @patch("social_network.file_structure_manager.get_path", return_value=Path("/valid/folder"))
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text", side_effect=PermissionError)
    def test_create_pointer_file_permission_error_on_write(
        self, _mock_write, _mock_mkdir, _mock_get_path
    ):
        record = self.valid_record.copy()
        result = file_structure_manager.create_pointer_file(record)
        self.assertFalse(result)

    @patch("social_network.file_structure_manager.get_path", return_value=Path("/valid/folder"))
    @patch("pathlib.Path.mkdir")
    @patch("pathlib.Path.write_text", side_effect=OSError("Disk full"))
    def test_create_pointer_file_oserror_on_write(
        self, _mock_write, _mock_mkdir, _mock_get_path
    ):
        record = self.valid_record.copy()
        result = file_structure_manager.create_pointer_file(record)
        self.assertFalse(result)
