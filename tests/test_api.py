# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring

import unittest
from unittest.mock import MagicMock, patch
from werkzeug.exceptions import NotFound
from social_network.api import app, UserRecord, StatusRecord, PictureRecord



class TestLookupUserByID(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

    def tearDown(self):
        self.app_context.pop()

    @patch.object(UserRecord, 'query')
    def test_get_user_success(self, mock_query):
        mock_query.filter_by.return_value.first_or_404.return_value = UserRecord(
            id=1,
            user_id='123',
            email='test@test.com',
            user_name='Test',
            user_last_name='McTest'
        )

        response = self.client.get('/users/123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                'id': 1,
                'user_id': '123',
                'email': 'test@test.com',
                'user_name': 'Test',
                'user_last_name': 'McTest',
            },
        )


    @patch.object(UserRecord, 'query')
    def test_get_user_not_found(self, mock_query):
        # Arrange: simulate .first_or_404() raising NotFound
        mock_query.filter_by.return_value.first_or_404.side_effect = NotFound()

        # Act
        response = self.client.get('/users/999')

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertIn('The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again', response.get_data(as_text=True))


class TestLookupStatusByUserID(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

    def tearDown(self):
        self.app_context.pop()


    @patch.object(StatusRecord, 'query')
    def test_get_status_success(self, mock_query):
        mock_query.filter_by.return_value.first_or_404.return_value = StatusRecord(
            id=1,
            status_id='s123',
            user_id='u123',
            status_text='test',
        )

        response = self.client.get('/statuses/s123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                'id': 1,
                'status_id': 's123',
                'user_id': 'u123',
                'status_text': 'test',
            },
        )


    @patch.object(StatusRecord, 'query')
    def test_get_status_not_found(self, mock_query):
        # Arrange: simulate .first_or_404() raising NotFound
        mock_query.filter_by.return_value.first_or_404.side_effect = NotFound()

        # Act
        response = self.client.get('/statuses/999')

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertIn('The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again', response.get_data(as_text=True))

class TestLookupPictureByUserID(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()

    def tearDown(self):
        self.app_context.pop()


    @patch.object(PictureRecord, 'query')
    def test_get_picture_success(self, mock_query):
        mock_query.filter_by.return_value.first_or_404.return_value = PictureRecord(
            id=1,
            picture_id='p123',
            user_id='u123',
            tags='#a',
            file_name='',
        )

        response = self.client.get('/images/p123')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                'id': 1,
                'picture_id': 'p123',
                'user_id': 'u123',
                'tags': '#a',
                'file_name': '',
            },
        )
