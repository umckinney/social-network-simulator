# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring

from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open
from social_network.main import (
    load_users,
    load_status_updates,
    add_user,
    update_user,
    delete_user,
    search_user,
    add_status,
    update_status,
    delete_status,
    search_status,
)


class TestMainLoadFunctions(TestCase):

    def setUp(self):
        self.mock_user_table = MagicMock()
        self.mock_status_table = MagicMock()
        self.mock_picture_table = MagicMock()

    @patch("social_network.main.add_user_logic", return_value=True)
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="USER_ID,EMAIL,NAME,LASTNAME\nU001,test@test.com,Test,McTest\n",
    )
    def test_load_users_success(self, _mock_file, mock_add_user):
        result = load_users("fake_users.csv", self.mock_user_table)
        self.assertTrue(result)
        mock_add_user.assert_called_once()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="BAD_FIELD,EMAIL,NAME,LASTNAME\n",
    )
    def test_load_users_missing_required_fields(self, _mock_file):
        result = load_users("fake_users.csv", self.mock_user_table)
        self.assertFalse(result)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_users_file_not_found(self, _mock_file):
        result = load_users("missing_file.csv", self.mock_user_table)
        self.assertFalse(result)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="STATUS_ID,USER_ID,STATUS_TEXT\nS001,U001,Hello World\n",
    )
    @patch("social_network.main.add_status_logic", return_value=True)
    def test_load_status_updates_success(self, mock_add_status, _mock_file):
        result = load_status_updates(
            "fake_status.csv", self.mock_user_table, self.mock_status_table
        )
        self.assertTrue(result)
        mock_add_status.assert_called_once()

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="BAD_HEADER,USER_ID,STATUS_TEXT\n",
    )
    def test_load_status_updates_missing_fields(self, _mock_file):
        result = load_status_updates(
            "fake_status.csv", self.mock_user_table, self.mock_status_table
        )
        self.assertFalse(result)

    @patch("builtins.open", side_effect=KeyError("missing key"))
    def test_load_status_updates_key_error(self, _mock_file):
        result = load_status_updates(
            "fake_status.csv", self.mock_user_table, self.mock_status_table
        )
        self.assertFalse(result)


class TestMainUserFunctions(TestCase):
    def setUp(self):
        self.user_table = MagicMock()
        self.status_table = MagicMock()
        self.picture_table = MagicMock()

        self.valid_user_data = {
            "user_id": "U001",
            "email": "test@example.com",
            "user_name": "Testy",
            "user_last_name": "McTestface",
        }

    @patch("social_network.main.add_user_logic", return_value=True)
    def test_add_user_happy(self, mock_add_user):
        result = add_user(self.valid_user_data, self.user_table)
        mock_add_user.assert_called_once_with(
            self.valid_user_data, self.valid_user_data["user_id"], table=self.user_table
        )
        self.assertTrue(result)

    @patch("social_network.main.add_user_logic", return_value=False)
    def test_add_user_sad(self, _mock_add_user):
        result = add_user(self.valid_user_data, self.user_table)
        self.assertFalse(result)

    @patch("social_network.main.update_user_logic", return_value=True)
    def test_update_user_happy(self, mock_update_user):
        result = update_user(self.valid_user_data, self.user_table)
        mock_update_user.assert_called_once_with(
            self.valid_user_data, self.valid_user_data["user_id"], table=self.user_table
        )
        self.assertTrue(result)

    @patch("social_network.main.update_user_logic", return_value=False)
    def test_update_user_sad(self, mock_update_user):
        result = mock_update_user(self.valid_user_data, self.user_table)
        self.assertFalse(result)

    @patch("social_network.domain_logic_layer.delete_statuses_by_user", return_value=True)
    @patch("social_network.domain_logic_layer.delete_user_core", return_value=True)
    def test_delete_user_happy(
        self, mock_delete_user_core, mock_delete_statuses_by_user
    ):
        result = delete_user(
            "U001", self.user_table, self.status_table, self.picture_table
        )
        mock_delete_statuses_by_user.assert_called_once_with(
            record_id="U001", table=self.status_table
        )
        mock_delete_user_core.assert_called_once_with(
            record_id="U001", table=self.user_table
        )
        self.assertTrue(result)

    @patch("social_network.main.delete_user_logic", return_value=False)
    def test_delete_user_status_delete_fails(self, _mock_delete_status):
        result = delete_user(
            "U001", self.user_table, self.status_table, self.picture_table
        )
        self.assertFalse(result)

    @patch("social_network.main.search_user_logic")
    def test_search_user_found(self, mock_search_user):
        mock_user = {
            "user_id": "U001",
            "email": "test@example.com",
            "user_name": "Testy",
            "user_last_name": "McTestface",
        }
        mock_search_user.return_value = mock_user
        result = search_user("U001", self.user_table)
        mock_search_user.assert_called_once_with("U001", table=self.user_table)
        self.assertEqual(result["user_id"], "U001")

    @patch("social_network.main.search_user_logic", return_value=None)
    def test_search_user_not_found(self, _mock_search_user):
        result = search_user("U001", self.user_table)
        self.assertIsNone(result)


class TestMainStatusFunctions(TestCase):
    def setUp(self):
        self.user_table = MagicMock()
        self.status_table = MagicMock()
        self.valid_status_data = {
            "status_id": "S001",
            "user_id": "U001",
            "status_text": "All systems go!",
        }

    @patch("social_network.domain_logic_layer.add_status_core", return_value=True)
    @patch("social_network.domain_logic_layer.search_user", return_value=True)
    def test_add_status_happy(self, mock_search_user, mock_add_status_core):
        result = add_status(self.valid_status_data, self.user_table, self.status_table)
        mock_search_user.assert_called_once_with("U001", table=self.user_table)
        mock_add_status_core.assert_called_once_with(
            self.valid_status_data, "S001", table=self.status_table
        )
        self.assertTrue(result)

    @patch("social_network.main.search_user_logic", return_value=None)
    def test_add_status_user_not_found(self, _mock_search_user):
        result = add_status(self.valid_status_data, self.user_table, self.status_table)
        self.assertFalse(result)

    @patch("social_network.main.update_status_logic", return_value=True)
    def test_update_status_happy(self, mock_update_status):
        result = update_status(
            self.valid_status_data, self.user_table, self.status_table
        )
        mock_update_status.assert_called_once_with(
            self.valid_status_data, "S001", table=self.status_table
        )
        self.assertTrue(result)

    @patch("social_network.main.update_status_logic", return_value=False)
    def test_update_status_sad(self, _mock_modify_status):
        result = update_status(
            self.valid_status_data, self.user_table, self.status_table
        )
        self.assertFalse(result)

    @patch("social_network.main.delete_status_logic", return_value=True)
    def test_delete_status_happy(self, mock_delete_status):
        result = delete_status("S001", self.status_table)
        mock_delete_status.assert_called_once_with("S001", table=self.status_table)
        self.assertTrue(result)

    @patch("social_network.main.delete_status_logic", return_value=False)
    def test_delete_status_sad(self, _mock_delete_status):
        result = delete_status("S001", self.status_table)
        self.assertFalse(result)

    @patch("social_network.main.search_status_logic")
    def test_search_status_found(self, mock_search_status):
        mock_status = {
            "status_id": "S001",
            "user_id": "U001",
            "status_text": "All systems go!",
        }
        mock_search_status.return_value = mock_status
        result = search_status("S001", self.status_table)
        mock_search_status.assert_called_once_with("S001", table=self.status_table)
        self.assertEqual(result["status_text"], "All systems go!")

    @patch("social_network.main.search_status_logic", return_value=None)
    def test_search_status_not_found(self, _mock_search_status):
        result = search_status("S001", self.status_table)
        self.assertIsNone(result)
