# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring

from functools import lru_cache
import unittest
from unittest.mock import MagicMock, patch
from peewee import IntegrityError, OperationalError
import social_network.socialnetwork_model as socialnetwork_model


class TestSocialNetworkModel(unittest.TestCase):
    def test_get_user_table(self):
        mock_db = MagicMock()
        result = socialnetwork_model.get_user_table(mock_db)
        mock_db.__getitem__.assert_called_once_with("UserTable")
        self.assertEqual(result, mock_db.__getitem__.return_value)

    def test_get_status_table(self):
        mock_db = MagicMock()
        result = socialnetwork_model.get_status_table(mock_db)
        mock_db.__getitem__.assert_called_once_with("StatusTable")
        self.assertEqual(result, mock_db.__getitem__.return_value)

    def test_get_picture_table(self):
        mock_db = MagicMock()
        result = socialnetwork_model.get_picture_table(mock_db)
        mock_db.__getitem__.assert_called_once_with("PictureTable")
        self.assertEqual(result, mock_db.__getitem__.return_value)

    @patch("social_network.socialnetwork_model.get_picture_table")
    @patch("social_network.socialnetwork_model.get_status_table")
    @patch("social_network.socialnetwork_model.get_user_table")
    @patch("social_network.socialnetwork_model.database_manager")
    def test_initialize_database(
        self,
        mock_database_manager,
        mock_get_user_table,
        mock_get_status_table,
        mock_get_picture_table,
    ):
        mock_db = MagicMock()
        mock_user_table = MagicMock()
        mock_status_table = MagicMock()
        mock_picture_table = MagicMock()

        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_db
        mock_cm.__exit__.return_value = None
        mock_database_manager.return_value = mock_cm

        mock_get_user_table.return_value = mock_user_table
        mock_get_status_table.return_value = mock_status_table
        mock_get_picture_table.return_value = mock_picture_table

        users, status, picture = socialnetwork_model.initialize_database()

        mock_database_manager.assert_called_once()
        mock_get_user_table.assert_called_once_with(mock_db)
        mock_get_status_table.assert_called_once_with(mock_db)
        mock_get_picture_table.assert_called_once_with(mock_db)

        mock_user_table.insert.assert_called_once()
        mock_user_table.create_index.assert_called_once_with(["user_id"], unique=True)
        mock_status_table.insert.assert_called_once()
        mock_status_table.create_index.assert_called_once_with(
            ["status_id"], unique=True
        )
        mock_picture_table.insert.assert_called_once()
        mock_picture_table.create_index.assert_called_once_with(
            ["picture_id"], unique=True
        )

        mock_user_table.delete.assert_called_once_with(user_id="<USER_ID>")
        mock_status_table.delete.assert_called_once_with(status_id="<STATUS_ID>")
        mock_picture_table.delete.assert_called_once_with(picture_id="<PICTURE_ID>")

        self.assertEqual(users, mock_user_table)
        self.assertEqual(status, mock_status_table)
        self.assertEqual(picture, mock_picture_table)

    @patch("social_network.socialnetwork_model.get_picture_table")
    @patch("social_network.socialnetwork_model.get_status_table")
    @patch("social_network.socialnetwork_model.get_user_table")
    @patch("social_network.socialnetwork_model.DataSet")
    def test_initialize_database_user_insert_error(
        self,
        mock_dataset,
        mock_get_user_table,
        mock_get_status_table,
        mock_get_picture_table,
    ):
        mock_db = MagicMock()
        mock_user_table = MagicMock()
        mock_status_table = MagicMock()
        mock_picture_table = MagicMock()

        mock_dataset.return_value = mock_db
        mock_get_user_table.return_value = mock_user_table
        mock_get_status_table.return_value = mock_status_table
        mock_get_picture_table.return_value = mock_picture_table

        mock_user_table.insert.side_effect = IntegrityError("insert failed")

        socialnetwork_model.initialize_database()

        mock_user_table.insert.assert_called_once()
        mock_status_table.insert.assert_called_once()
        mock_picture_table.insert.assert_called_once()

    @patch("social_network.socialnetwork_model.get_status_table")
    @patch("social_network.socialnetwork_model.get_user_table")
    @patch("social_network.socialnetwork_model.DataSet")
    def test_initialize_database_status_insert_error(
        self, mock_dataset, mock_get_user_table, mock_get_status_table
    ):
        mock_db = MagicMock()
        mock_user_table = MagicMock()
        mock_status_table = MagicMock()

        mock_dataset.return_value = mock_db
        mock_get_user_table.return_value = mock_user_table
        mock_get_status_table.return_value = mock_status_table

        mock_get_user_table.return_value = mock_user_table
        mock_status_table.insert.side_effect = IntegrityError("insert failed")

        socialnetwork_model.initialize_database()

        mock_user_table.insert.assert_called_once()
        mock_status_table.insert.assert_called_once()

    @patch("social_network.socialnetwork_model.get_status_table")
    @patch("social_network.socialnetwork_model.get_user_table")
    @patch("social_network.socialnetwork_model.DataSet")
    def test_initialize_database_delete_status_error(
        self, mock_dataset, mock_get_user_table, mock_get_status_table
    ):
        mock_db = MagicMock()
        mock_user_table = MagicMock()
        mock_status_table = MagicMock()

        mock_dataset.return_value = mock_db
        mock_get_user_table.return_value = mock_user_table
        mock_get_status_table.return_value = mock_status_table

        mock_status_table.delete.side_effect = OperationalError("status delete failed")

        socialnetwork_model.initialize_database()

        mock_user_table.delete.assert_called_once()
        mock_status_table.delete.assert_called_once()

    @patch("social_network.socialnetwork_model.get_status_table")
    @patch("social_network.socialnetwork_model.get_user_table")
    @patch("social_network.socialnetwork_model.DataSet")
    def test_initialize_database_user_delete_error(
        self, mock_dataset, mock_get_user_table, mock_get_status_table
    ):
        mock_db = MagicMock()
        mock_user_table = MagicMock()
        mock_status_table = MagicMock()

        mock_dataset.return_value = mock_db
        mock_get_user_table.return_value = mock_user_table
        mock_get_status_table.return_value = mock_status_table

        mock_user_table.delete.side_effect = OperationalError("user delete failed")

        socialnetwork_model.initialize_database()

        mock_user_table.delete.assert_called_once()
        mock_status_table.delete.assert_called_once()

    @patch("social_network.socialnetwork_model.database_manager")
    def test_database_manager_success(self, mock_database_manager):
        mock_db = MagicMock()

        # Create a context manager mock that yields mock_db
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_db
        mock_cm.__exit__.return_value = None
        mock_database_manager.return_value = mock_cm

        if hasattr(socialnetwork_model.initialize_database, "cache_clear"):
            socialnetwork_model.initialize_database.cache_clear()

        with socialnetwork_model.database_manager() as db:
            self.assertEqual(db, mock_db)

        mock_database_manager.assert_called_once()

    @patch(
        "social_network.socialnetwork_model.database_manager", side_effect=OperationalError("DB error")
    )
    def test_database_manager_operational_error(self, _mock_dataset):
        if hasattr(socialnetwork_model.initialize_database, "cache_clear"):
            socialnetwork_model.initialize_database.cache_clear()

        with self.assertRaises(OperationalError):
            with socialnetwork_model.database_manager():
                pass
