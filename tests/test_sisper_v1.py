import unittest
from unittest.mock import patch, MagicMock, ANY
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sisper_v1 import create_app

class TestSisperV1App(unittest.TestCase):
    def setUp(self):
        """Set up test client and mock database"""
        # Mock the database connection
        self.db_patcher = patch('sisper_v1.db.get_db_conn')
        self.mock_get_db = self.db_patcher.start()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_get_db.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

        # Create test client
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after each test"""
        self.db_patcher.stop()
        self.app_context.pop()

    def test_app_creation(self):
        """Test that the app is created with the correct configuration"""
        app = create_app()
        self.assertTrue(app.config['TESTING'] is False)  # Default is False
        self.assertIn('SECRET_KEY', app.config)

    def test_home_page_redirects_to_login(self):
        """Test that the home page redirects to login when not authenticated"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect status
        self.assertIn('/login', response.location)

    def test_login_page_loads(self):
        """Test that the login page loads correctly"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    @patch('sisper_v1.blueprints.auth.auth.publish_mahasiswa_event')
    def test_login_success(self, mock_publish):
        """Test successful login"""
        # Mock database response for login
        self.mock_cursor.fetchone.return_value = {
            'nim': '12345',
            'password': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # 'password' hashed
            'nama': 'Test User',
            'jenis': 'mahasiswa'
        }

        response = self.client.post('/login', data={
            'nim': '12345',
            'password': 'password',
            'jenis': 'mahasiswa'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
        mock_publish.assert_called_once()

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        self.mock_cursor.fetchone.return_value = None

        response = self.client.post('/login', data={
            'nim': 'wrong',
            'password': 'wrong',
            'jenis': 'mahasiswa'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        self.assertIn(b'Invalid credentials', response.data)

    @patch('sisper_v1.blueprints.auth.auth.publish_mahasiswa_event')
    def test_logout(self, mock_publish):
        """Test logout functionality"""
        # First login
        self.mock_cursor.fetchone.return_value = {
            'nim': '12345',
            'password': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
            'nama': 'Test User',
            'jenis': 'mahasiswa'
        }
        self.client.post('/login', data={
            'nim': '12345',
            'password': 'password',
            'jenis': 'mahasiswa'
        })

        # Then logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_protected_route_requires_login(self):
        """Test that protected routes redirect to login when not authenticated"""
        response = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    @patch('sisper_v1.blueprints.buku.buku.get_db_conn')
    def test_get_books(self, mock_db_conn):
        """Test getting list of books"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'isbn': '123', 'judul': 'Test Book', 'penulis': 'Author'}
        ]

        # Login first
        with self.client.session_transaction() as sess:
            sess['nim'] = '12345'
            sess['nama'] = 'Test User'

        response = self.client.get('/buku')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Book', response.data)

    @patch('sisper_v1.blueprints.peminjaman.peminjaman.get_db_conn')
    def test_borrow_book(self, mock_db_conn):
        """Test borrowing a book"""
        # Setup mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'isbn': '123', 'judul': 'Test Book'}

        # Login first
        with self.client.session_transaction() as sess:
            sess['nim'] = '12345'
            sess['nama'] = 'Test User'

        response = self.client.post('/pinjam', data={
            'isbn': '123',
            'tanggal_pinjam': '2025-01-01',
            'tanggal_kembali': '2025-01-08'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Peminjaman berhasil', response.data)

if __name__ == '__main__':
    unittest.main()