from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class APIRegionsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )
        from core.models import ChinaRegion
        self.province = ChinaRegion.objects.create(
            code='440000',
            name='广东省',
            level=1
        )

    def test_api_provinces_requires_login(self):
        response = self.client.get('/api/regions/provinces/')
        self.assertEqual(response.status_code, 302)

    def test_api_provinces_authenticated(self):
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/api/regions/provinces/')
        self.assertEqual(response.status_code, 200)

    def test_api_cities_requires_login(self):
        response = self.client.get('/api/regions/cities/?province=440000')
        self.assertEqual(response.status_code, 302)

    def test_api_cities_authenticated(self):
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/api/regions/cities/?province=440000')
        self.assertEqual(response.status_code, 200)

    def test_api_districts_requires_login(self):
        response = self.client.get('/api/regions/districts/?city=440100')
        self.assertEqual(response.status_code, 302)

    def test_api_districts_authenticated(self):
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/api/regions/districts/?city=440100')
        self.assertEqual(response.status_code, 200)

    def test_api_search_requires_login(self):
        response = self.client.get('/api/regions/search/?keyword=广东')
        self.assertEqual(response.status_code, 302)

    def test_api_search_authenticated(self):
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/api/regions/search/?keyword=广东')
        self.assertIn(response.status_code, [200, 400])


class APITimeTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )

    def test_api_time_requires_login(self):
        response = self.client.get('/api/time/current/')
        self.assertEqual(response.status_code, 302)

    def test_api_time_authenticated(self):
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/api/time/current/')
        self.assertEqual(response.status_code, 200)


class APITaxonomyTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test12345678'
        )

    def test_admin_taxonomy_list_requires_login(self):
        response = self.client.get('/admin/taxonomies/')
        self.assertEqual(response.status_code, 302)

    def test_admin_taxonomy_list_authenticated(self):
        self.client.login(username='testuser', password='test12345678')
        response = self.client.get('/admin/taxonomies/')
        self.assertIn(response.status_code, [200, 302])