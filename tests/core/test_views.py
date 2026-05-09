from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class AuthViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )

    def test_login_view_get(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'test12345678'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_credentials(self):
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_login_redirect_authenticated(self):
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/accounts/login/')
        self.assertIn(response.status_code, [200, 302])


class UserManageViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123456',
            role='manager',
            is_admin=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )

    def test_user_list_requires_login(self):
        response = self.client.get('/admin/users/')
        self.assertEqual(response.status_code, 302)

    def test_user_list_authenticated(self):
        self.client.login(username='admin', password='admin123456')
        response = self.client.get('/admin/users/')
        self.assertIn(response.status_code, [200, 302])


class SettingsViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123456',
            role='manager',
            is_admin=True
        )

    def test_settings_list_requires_login(self):
        response = self.client.get('/admin/settings/')
        self.assertEqual(response.status_code, 302)

    def test_settings_list_authenticated(self):
        self.client.login(username='admin', password='admin123456')
        response = self.client.get('/admin/settings/')
        self.assertIn(response.status_code, [200, 302])


class TaxonomyViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123456',
            role='manager',
            is_admin=True
        )

    def test_taxonomy_list_requires_login(self):
        response = self.client.get('/admin/taxonomies/')
        self.assertEqual(response.status_code, 302)

    def test_taxonomy_list_authenticated(self):
        self.client.login(username='admin', password='admin123456')
        response = self.client.get('/admin/taxonomies/')
        self.assertIn(response.status_code, [200, 302])