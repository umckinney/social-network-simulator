# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring

import unittest
from unittest.mock import MagicMock, patch
from peewee import IntegrityError
from social_network.data_access_layer import (
    get_object,
    get_objects,
    add_object,
    update_object,
    delete_object,
    delete_objects,
)

TEST_RECORD = {
    "user_id": "u01",
    "email": "test@example.com",
    "user_name": "Test",
    "user_last_name": "McTest",
}
UPDATED_TEST_RECORD = {
    "user_id": "u01",
    "email": "updated-test@example.com",
    "user_name": "Updated Test",
    "user_last_name": "Updated McTest",
}


class TestDataAccessLayer(unittest.TestCase):
    def test_get_object_found(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = TEST_RECORD
        result = get_object("u01", field_name="user_id", table=mock_table)
        mock_table.find_one.assert_called_once_with(user_id="u01")
        self.assertEqual(result, TEST_RECORD)

    def test_get_object_not_found(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = None
        result = get_object("u01", field_name="user_id", table=mock_table)
        mock_table.find_one.assert_called_once_with(user_id="u01")
        self.assertIsNone(result)

    def test_get_objects_values_returned(self):
        mock_table = MagicMock()
        mock_get_objects = MagicMock()
        mock_table.find.return_value = TEST_RECORD
        mock_get_objects.return_value = TEST_RECORD
        result = get_objects("u01", field_name="user_id", table=mock_table)
        mock_table.find.assert_called_once_with(user_id="u01")
        self.assertEqual(result, TEST_RECORD)

    def test_get_objects_no_values_returned(self):
        mock_table = MagicMock()
        mock_table.find.return_value = iter([])
        result = get_objects("u01", field_name="user_id", table=mock_table)
        mock_table.find.assert_called_once_with(user_id="u01")
        self.assertEqual(list(result), [])

    @patch("social_network.data_access_layer.get_object")
    def test_add_object_success(self, mock_get_object):
        mock_get_object.return_value = None
        mock_table = MagicMock()
        record_data = TEST_RECORD
        result = add_object(record_data, "u01", field_name="user_id", table=mock_table)
        self.assertTrue(result)
        mock_table.insert.assert_called_once_with(**record_data)

    @patch("social_network.data_access_layer.get_object")
    def test_add_object_duplicate(self, mock_get_object):
        mock_get_object.return_value = TEST_RECORD
        mock_table = MagicMock()
        record_data = TEST_RECORD
        result = add_object(record_data, "u01", field_name="user_id", table=mock_table)
        self.assertFalse(result)
        mock_table.insert.assert_not_called()

    @patch("social_network.data_access_layer.get_object")
    def test_add_object_integrity_error(self, mock_get_object):
        mock_get_object.return_value = None
        mock_table = MagicMock()
        mock_table.insert.side_effect = IntegrityError("db error")
        record_data = TEST_RECORD
        result = add_object(record_data, "u01", field_name="user_id", table=mock_table)
        self.assertFalse(result)
        mock_table.insert.assert_called_once_with(**record_data)

    @patch("social_network.data_access_layer.get_object")
    def test_update_object_success(self, mock_get_object):
        mock_get_object.return_value = TEST_RECORD

        mock_table = MagicMock()
        mock_update = mock_table.update.return_value
        mock_where = mock_update.where.return_value
        mock_where.execute.return_value = 1

        record_data = UPDATED_TEST_RECORD
        result = update_object(
            record_data, "u01", field_name="user_id", table=mock_table
        )
        self.assertTrue(result)

        expected_update_data = record_data.copy()
        expected_update_data.pop("user_id", None)
        mock_table.update.assert_called_once_with(**expected_update_data)

    @patch("social_network.data_access_layer.get_object")
    def test_update_object_not_found(self, mock_get_object):
        mock_get_object.return_value = None
        mock_table = MagicMock()
        record_data = UPDATED_TEST_RECORD
        result = update_object(
            record_data, "u01", field_name="user_id", table=mock_table
        )
        self.assertFalse(result)
        mock_table.update.assert_not_called()

    @patch("social_network.data_access_layer.get_object")
    def test_update_object_integrity_error(self, mock_get_object):
        mock_get_object.return_value = TEST_RECORD

        mock_table = MagicMock()
        mock_update = mock_table.update.return_value
        mock_where = mock_update.where.return_value
        mock_where.execute.side_effect = IntegrityError("Duplicate key error")

        record_data = UPDATED_TEST_RECORD
        result = update_object(
            record_data, "u01", field_name="user_id", table=mock_table
        )
        self.assertFalse(result)

        expected_update_data = record_data.copy()
        expected_update_data.pop("user_id", None)
        mock_table.update.assert_called_once_with(**expected_update_data)

    @patch("social_network.data_access_layer.get_object")
    def test_delete_object_success(self, mock_get_object):
        mock_table = MagicMock()
        mock_table.__name__ = "MockTable"
        mock_table.delete.return_value = 1

        mock_get_object.return_value = {"user_id": "u01"}

        result = delete_object("u01", field_name="user_id", table=mock_table)

        self.assertTrue(result)
        mock_table.delete.assert_called_once_with(user_id="u01")

    @patch("social_network.data_access_layer.get_object")
    def test_delete_object_not_found(self, mock_get_object):
        mock_get_object.return_value = None
        mock_table = MagicMock()
        result = delete_object("u01", field_name="user_id", table=mock_table)
        self.assertFalse(result)
        mock_table.delete.assert_not_called()

    @patch("social_network.data_access_layer.get_object")
    def test_delete_object_integrity_error(self, mock_get_object):
        mock_table = MagicMock()
        mock_table.__name__ = "MockTable"
        mock_get_object.return_value = {"user_id": "u01"}

        mock_table.delete.side_effect = IntegrityError()

        result = delete_object("u01", field_name="user_id", table=mock_table)

        self.assertFalse(result)
        mock_table.delete.assert_called_once_with(user_id="u01")

    @patch("social_network.data_access_layer.logger")
    def test_delete_objects_success(self, _mock_logger):
        mock_table = MagicMock()
        mock_table.__name__ = "MockTable"
        mock_table.delete.return_value = 2

        result = delete_objects("u01", field_name="user_id", table=mock_table)
        self.assertTrue(result)
        mock_table.delete.assert_called_once_with(user_id="u01")

    @patch("social_network.data_access_layer.logger")
    def test_delete_objects_success_0_results(self, _mock_logger):
        mock_table = MagicMock()
        mock_table.__name__ = "MockTable"
        mock_table.delete.return_value = 0

        result = delete_objects("u01", field_name="user_id", table=mock_table)
        self.assertTrue(result)
        mock_table.delete.assert_called_once_with(user_id="u01")

    @patch("social_network.data_access_layer.database_manager")
    def test_delete_objects_integrity_error(self, _mock_database_manager):
        mock_table = MagicMock()
        mock_table.__name__ = "MockTable"
        mock_table.delete.side_effect = IntegrityError()

        result = delete_objects("u01", field_name="user_id", table=mock_table)

        self.assertFalse(result)
        mock_table.delete.assert_called_once_with(user_id="u01")
