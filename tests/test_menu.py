# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring
from unittest import TestCase
from unittest.mock import patch, MagicMock

from social_network.menu import (
    load_users,
    load_status_updates,
    handle_add_user,
    handle_update_user,
    handle_search_user,
    handle_add_status,
    handle_update_status,
    handle_search_status,
    handle_delete_status,
    quit_program,
)


class TestMenuUserOptions(TestCase):

    def setUp(self):
        self.mock_user_table = MagicMock()
        self.mock_status_table = MagicMock()

    @patch(
        "social_network.menu.validated_input_collector", return_value=lambda: {"filename": "users.csv"}
    )
    @patch("social_network.main.load_users", return_value=True)
    def test_load_users_happy(self, _mock_load_users, _mock_input_collector):
        result = load_users(self.mock_user_table)
        self.assertTrue(result)

    @patch("social_network.menu.validated_input_collector", return_value=lambda: None)
    @patch("social_network.main.load_users", return_value=True)
    def test_load_users_sad(self, _mock_load_users, _mock_input_collector):
        result = load_users(self.mock_user_table)
        self.assertFalse(result)

    def test_handle_add_user_happy(self):
        user_data = {
            "user_id": "U001",
            "email": "test@test.com",
            "user_name": "Test",
            "user_last_name": "McTest",
        }
        with (
            patch("social_network.menu.get_user_input", return_value=user_data),
            patch("social_network.main.add_user", return_value=True) as mock_add_user,
        ):
            result = handle_add_user(self.mock_user_table)
            mock_add_user.assert_called_once_with(user_data, self.mock_user_table)
            self.assertTrue(result)

    def test_handle_add_user_sad(self):
        user_data = {
            "user_id": "",
            "email": "test@test.com",
            "user_name": "Test",
            "user_last_name": "McTest",
        }
        with (
            patch("social_network.menu.get_user_input", return_value=user_data),
            patch("social_network.main.add_user", return_value=False) as mock_add_user,
        ):
            result = handle_add_user(self.mock_user_table)
            mock_add_user.assert_called_once_with(user_data, self.mock_user_table)
            self.assertFalse(result)

    def test_handle_update_user_happy(self):
        user_data = {
            "user_id": "U001",
            "email": "test@test.com",
            "user_name": "Test",
            "user_last_name": "McTest",
        }
        with (
            patch("social_network.menu.get_user_input", return_value=user_data),
            patch("social_network.main.update_user", return_value=True) as mock_update_user,
        ):
            result = handle_update_user(self.mock_user_table)
            mock_update_user.assert_called_once_with(user_data, self.mock_user_table)
            self.assertTrue(result)

    def test_handle_search_user_happy(self):
        with (
            patch(
                "social_network.menu.validated_input_collector",
                return_value=lambda: {"user_id": "U001"},
            ),
            patch(
                "social_network.main.search_user",
                return_value={
                    "user_id": "U001",
                    "email": "test@test.com",
                    "user_name": "Test",
                    "user_last_name": "McTest",
                },
            ) as mock_search,
        ):
            result = handle_search_user(self.mock_user_table)
            mock_search.assert_called_once_with("U001", self.mock_user_table)
            self.assertTrue(result)

    def test_handle_search_user_sad(self):
        with (
            patch(
                "social_network.menu.validated_input_collector",
                return_value=lambda: {"user_id": "U001"},
            ),
            patch("social_network.main.search_user", return_value=None) as mock_search,
        ):
            result = handle_search_user(self.mock_user_table)
            mock_search.assert_called_once_with("U001", self.mock_user_table)
            self.assertFalse(result)


class TestMenuStatusOptions(TestCase):

    def setUp(self):
        self.mock_user_table = MagicMock()
        self.mock_status_table = MagicMock()

    @patch(
        "social_network.menu.validated_input_collector", return_value=lambda: {"filename": "users.csv"}
    )
    @patch("social_network.main.load_users", return_value=False)
    def test_load_users_sad(self, _mock_load_users, _mock_input_collector):
        result = load_users(self.mock_user_table)
        self.assertFalse(result)

    @patch("social_network.menu.validated_input_collector", return_value=lambda: None)
    @patch("social_network.main.load_status_updates", return_value=True)
    def test_load_status_updates_sad(
        self, _mock_load_status_updates, _mock_input_collector
    ):
        result = load_status_updates(self.mock_user_table, self.mock_status_table)
        self.assertFalse(result)

    def test_handle_add_status_happy(self):
        status_data = {
            "status_id": "S001",
            "user_id": "U001",
            "status_text": "Test Status",
        }
        with (
            patch("social_network.menu.get_status_input", return_value=status_data),
            patch("social_network.main.add_status", return_value=True) as mock_add_status,
        ):
            result = handle_add_status(self.mock_user_table, self.mock_status_table)
            mock_add_status.assert_called_once_with(
                status_data, self.mock_user_table, self.mock_status_table
            )
            self.assertTrue(result)

    def test_handle_update_status_sad(self):
        status_data = {
            "status_id": "S001",
            "user_id": "U001",
            "status_text": "Test Status",
        }
        with (
            patch("social_network.menu.get_status_input", return_value=status_data),
            patch("social_network.main.update_status", return_value=False) as mock_update,
        ):
            result = handle_update_status(self.mock_user_table, self.mock_status_table)
            mock_update.assert_called_once_with(
                status_data, self.mock_user_table, self.mock_status_table
            )
            self.assertFalse(result)

    def test_handle_search_status_happy(self):
        mock_result = {
            "status_id": "S001",
            "user_id": "U001",
            "status_text": "Test Status",
        }
        with (
            patch(
                "social_network.menu.validated_input_collector",
                return_value=lambda: {"status_id": "S001"},
            ),
            patch("social_network.main.search_status", return_value=mock_result) as mock_search,
        ):
            result = handle_search_status(self.mock_status_table)
            mock_search.assert_called_once_with("S001", self.mock_status_table)
            self.assertTrue(result)

    def test_handle_delete_status_sad(self):
        with (
            patch(
                "social_network.menu.validated_input_collector",
                return_value=lambda: {"status_id": "S001"},
            ),
            patch("social_network.main.delete_status", return_value=False) as mock_delete,
        ):
            result = handle_delete_status(self.mock_status_table)
            mock_delete.assert_called_once_with("S001", self.mock_status_table)
            self.assertFalse(result)


class TestQuitProgram(TestCase):
    def test_quit_program_calls_sys_exit(self):
        with patch("sys.exit") as mock_exit:
            quit_program()
            mock_exit.assert_called_once()
