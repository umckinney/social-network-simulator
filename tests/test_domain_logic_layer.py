# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring

import unittest
from unittest.mock import MagicMock, patch

from social_network.domain_logic_layer import (
    add_user,
    update_user,
    delete_user,
    search_user,
    add_status,
    update_status,
    delete_status,
    search_status,
    add_picture,
    generate_normalized_filename,
)

TEST_USER_RECORD = {
    "user_id": "u01",
    "email": "test@example.com",
    "user_name": "Test",
    "user_last_name": "McTest",
}
UPDATED_TEST_USER_RECORD = {
    "user_id": "u01",
    "email": "updated-test@example.com",
    "user_name": "Updated Test",
    "user_last_name": "Updated McTest",
}
TEST_STATUS_RECORD = {
    "status_id": "s01",
    "user_id": "u01",
    "status_text": "Hello World!",
}
UPDATED_TEST_STATUS_RECORD = {
    "status_id": "s01",
    "user_id": "u01",
    "status_text": "Goodbye World!",
}


class TestDomainLogicLayer(
    unittest.TestCase
):  # pylint: disable=too-many-public-methods
    def test_add_user_inserts_when_not_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = None
        result = add_user(
            TEST_USER_RECORD, TEST_USER_RECORD["user_id"], table=mock_table
        )
        self.assertTrue(result)
        mock_table.insert.assert_called_once_with(**TEST_USER_RECORD)

    def test_add_user_inserts_when_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = TEST_USER_RECORD
        result = add_user(
            TEST_USER_RECORD, TEST_USER_RECORD["user_id"], table=mock_table
        )
        self.assertFalse(result)
        mock_table.insert.assert_not_called()

    def test_update_user_inserts_when_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = TEST_USER_RECORD
        mock_table.update.return_value.where.return_value.execute.return_value = 1

        result = update_user(
            UPDATED_TEST_USER_RECORD,
            UPDATED_TEST_USER_RECORD["user_id"],
            table=mock_table,
        )

        self.assertTrue(result)
        expected_update_data = UPDATED_TEST_USER_RECORD.copy()
        expected_update_data.pop("user_id")
        mock_table.update.assert_called_once_with(**expected_update_data)

    def test_update_user_inserts_when_not_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = None
        result = update_user(
            UPDATED_TEST_USER_RECORD,
            UPDATED_TEST_USER_RECORD["user_id"],
            table=mock_table,
        )
        self.assertFalse(result)
        mock_table.update.assert_not_called()

    def test_search_user_when_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = TEST_USER_RECORD
        result = search_user(TEST_USER_RECORD["user_id"], table=mock_table)
        self.assertTrue(result)
        mock_table.find_one.assert_called_once_with(user_id=TEST_USER_RECORD["user_id"])

    def test_search_user_when_not_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = None
        result = search_user(TEST_USER_RECORD["user_id"], table=mock_table)
        self.assertFalse(result)
        mock_table.find_one.assert_called_once_with(user_id=TEST_USER_RECORD["user_id"])

    def test_update_status_inserts_when_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = TEST_STATUS_RECORD
        mock_table.update.return_value.where.return_value.execute.return_value = 1

        result = update_status(
            UPDATED_TEST_STATUS_RECORD,
            UPDATED_TEST_STATUS_RECORD["status_id"],
            table=mock_table,
        )

        self.assertTrue(result)

        expected_update_data = UPDATED_TEST_STATUS_RECORD.copy()
        expected_update_data.pop("status_id")
        mock_table.update.assert_called_once_with(**expected_update_data)

    def test_update_status_when_not_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = None
        result = update_status(
            UPDATED_TEST_STATUS_RECORD,
            UPDATED_TEST_STATUS_RECORD["status_id"],
            table=mock_table,
        )
        self.assertFalse(result)
        mock_table.update.assert_not_called()

    @patch("social_network.domain_logic_layer.get_object")
    def test_delete_status_when_exists(self, mock_get_object):
        mock_table = MagicMock()
        mock_table.delete.return_value = 1
        mock_get_object.return_value = TEST_STATUS_RECORD

        result = delete_status("status01", table=mock_table)

        self.assertTrue(result)
        mock_table.delete.assert_called_once_with(status_id="status01")

    def test_delete_status_when_not_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = None
        result = delete_status(TEST_STATUS_RECORD["status_id"], table=mock_table)
        self.assertFalse(result)
        mock_table.delete.assert_not_called()

    def test_search_status_when_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = TEST_STATUS_RECORD
        result = search_status(TEST_STATUS_RECORD["status_id"], table=mock_table)
        self.assertTrue(result)
        mock_table.find_one.assert_called_once_with(
            status_id=TEST_STATUS_RECORD["status_id"]
        )

    def test_search_status_when_not_exists(self):
        mock_table = MagicMock()
        mock_table.find_one.return_value = None
        result = search_status(TEST_STATUS_RECORD["status_id"], table=mock_table)
        self.assertFalse(result)
        mock_table.find_one.assert_called_once_with(
            status_id=TEST_STATUS_RECORD["status_id"]
        )

    @patch("social_network.domain_logic_layer.delete_statuses_by_user")
    @patch("social_network.domain_logic_layer.delete_user_core")
    def test_delete_user_success(
        self, mock_delete_user_core, mock_delete_statuses_by_user
    ):
        mock_delete_user_core.return_value = True
        mock_delete_statuses_by_user.return_value = True
        result = delete_user(
            TEST_USER_RECORD["user_id"],
            user_table=MagicMock(),
            status_table=MagicMock(),
            picture_table=MagicMock(),
        )
        self.assertTrue(result)
        mock_delete_statuses_by_user.assert_called_once()
        mock_delete_user_core.assert_called_once()

    @patch("social_network.domain_logic_layer.delete_statuses_by_user")
    @patch("social_network.domain_logic_layer.delete_user_core")
    def test_delete_user_fails_user_delete(
        self, mock_delete_user_core, mock_delete_statuses_by_user
    ):
        mock_delete_user_core.return_value = False
        mock_delete_statuses_by_user.return_value = True
        result = delete_user(
            TEST_USER_RECORD["user_id"],
            user_table=MagicMock(),
            status_table=MagicMock(),
            picture_table=MagicMock(),
        )
        self.assertFalse(result)

    @patch("social_network.domain_logic_layer.search_user")
    @patch("social_network.domain_logic_layer.add_status_core")
    def test_add_status_success(self, mock_add_status_core, mock_search_user):
        mock_search_user.return_value = True
        mock_add_status_core.return_value = True
        result = add_status(
            TEST_STATUS_RECORD, user_table=MagicMock(), status_table=MagicMock()
        )
        self.assertTrue(result)
        mock_add_status_core.assert_called_once()

    @patch("social_network.domain_logic_layer.search_user")
    @patch("social_network.domain_logic_layer.add_status_core")
    def test_add_status_user_not_found(self, mock_add_status_core, mock_search_user):
        mock_search_user.return_value = None
        result = add_status(
            TEST_STATUS_RECORD, user_table=MagicMock(), status_table=MagicMock()
        )
        self.assertFalse(result)
        mock_add_status_core.assert_not_called()

    @patch("social_network.domain_logic_layer.update_picture", return_value=True)
    @patch("social_network.domain_logic_layer.get_object")
    @patch("social_network.domain_logic_layer.add_picture_core")
    @patch("social_network.domain_logic_layer.search_user", return_value=True)
    def test_add_picture_success_with_tags_and_uuid(
        self,
        _mock_search_user,
        _mock_add_picture_core,
        mock_get_object,
        _mock_update_picture,
    ):
        picture_data = {"user_id": "u01", "tags": "#foo #bar"}

        returned_record = {
            "picture_id": "mock_id",
            "user_id": "u01",
            "tags": ["foo", "bar"],
            "id": 42,
        }

        _mock_add_picture_core.return_value = returned_record
        mock_get_object.return_value = returned_record

        try:
            result = add_picture(
                picture_data, user_table=MagicMock(), picture_table=MagicMock()
            )
        except Exception as e:
            print(f"Exception: {e}")
            raise

        self.assertTrue(result)
        self.assertEqual(result["user_id"], "u01")

    @patch("social_network.domain_logic_layer.get_object")
    def test_add_picture_user_not_found(self, mock_get_object):
        mock_get_object.return_value = False

        user_table = MagicMock()
        picture_table = MagicMock()

        picture_data = {"user_id": "missing_user", "tags": "#a #b"}

        result = add_picture(picture_data, user_table, picture_table)
        self.assertFalse(result)

    @patch("social_network.domain_logic_layer.get_object")
    @patch("social_network.domain_logic_layer.add_picture_core")
    def test_add_picture_insert_fails(self, mock_add_picture_core, mock_get_object):
        mock_get_object.return_value = True
        mock_add_picture_core.return_value = False

        user_table = MagicMock()
        picture_table = MagicMock()

        picture_data = {"user_id": "u01", "tags": "#x #y"}

        result = add_picture(picture_data, user_table, picture_table)
        self.assertFalse(result)

    def test_generate_normalized_filename_default_extension(self):
        result = generate_normalized_filename(42)
        self.assertEqual(result, "0000000042.png")

    def test_generate_normalized_filename_custom_extension(self):
        result = generate_normalized_filename(7, extension="txt")
        self.assertEqual(result, "0000000007.txt")
