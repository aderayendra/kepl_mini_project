import unittest
from unittest.mock import patch, MagicMock, ANY
import json
import sys
import os

# Add service path to sys.path
SERVICE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sisper_v2', 'services', 'buku'))
sys.path.append(SERVICE_PATH)

# Mock redis before importing app
with patch('redis.Redis'):
    from app import app


class TestBukuService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.sample_book = {
            "isbn": "1234567890",
            "judul": "Test Book",
            "penulis": "Test Author",
            "kategori": "Test Category",
            "sinopsis": "Test Synopsis",
            "tahun": 2023
        }

    @patch('app.get_db_conn')
    @patch('app.publish_book_event')
    def test_get_all_buku(self, mock_publish, mock_get_db_conn):
        """Test getting all books"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {"isbn": "123", "judul": "Buku A", "waktu_edit": None, "waktu_input": None, "waktu_hapus": None},
            {"isbn": "456", "judul": "Buku B", "waktu_edit": None, "waktu_input": None, "waktu_hapus": None}
        ]

        response = self.app.post('/buku', json={})
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['judul'], "Buku A")
        mock_publish.assert_not_called()

    @patch('app.get_db_conn')
    @patch('app.publish_book_event')
    def test_search_buku(self, mock_publish, mock_get_db_conn):
        """Test searching for books"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {"isbn": "123", "judul": "Buku A", "waktu_edit": None, "waktu_input": None, "waktu_hapus": None}
        ]

        response = self.app.post('/buku', json={'s': 'Buku A', 'nim': '1001'})
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        mock_publish.assert_called_once_with("book_searched", {"nim": "1001", "keyword": "Buku A"})

    @patch('app.get_db_conn')
    @patch('app.publish_book_event')
    def test_tambah_buku_success(self, mock_publish, mock_get_db_conn):
        """Test adding a new book successfully"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.app.post('/buku/tambah', json=self.sample_book)
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['message'], "Buku berhasil ditambahkan")
        mock_publish.assert_called_once_with("book_added", self.sample_book)

    @patch('app.get_db_conn')
    def test_tambah_buku_missing_fields(self, mock_get_db_conn):
        """Test adding a book with missing required fields"""
        response = self.app.post('/buku/tambah', json={"judul": "Incomplete Book"})
        data = response.get_json()

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", data)

    @patch('app.get_db_conn')
    @patch('app.publish_book_event')
    def test_edit_buku(self, mock_publish, mock_get_db_conn):
        """Test editing a book"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        update_data = {
            "isbn_original": "123",
            "judul": "Updated Title",
            "penulis": "Updated Author",
            "kategori": "Updated Category",
            "sinopsis": "Updated Synopsis",
            "tahun": 2024
        }

        response = self.app.post('/buku/edit', json=update_data)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Buku berhasil diupdate!")
        mock_publish.assert_called_once_with("book_updated", update_data)

    @patch('app.get_db_conn')
    @patch('app.publish_book_event')
    def test_hapus_buku(self, mock_publish, mock_get_db_conn):
        """Test deleting a book"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.app.delete('/buku/hapus?isbn=123')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], "Buku berhasil dihapus!")
        mock_publish.assert_called_once_with("book_deleted", {"isbn": "123"})

    @patch('app.get_db_conn')
    def test_hapus_buku_missing_isbn(self, mock_get_db_conn):
        """Test deleting a book without providing ISBN"""
        response = self.app.delete('/buku/hapus')
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "ISBN is required")


if __name__ == '__main__':
    unittest.main()
