from django.test import TestCase
from core.forms.auth_forms import LoginForm


class LoginFormTestCase(TestCase):
    def test_login_form_valid_data(self):
        form = LoginForm(data={
            'username': 'testuser',
            'password': 'test12345678'
        })
        self.assertTrue(form.is_valid())

    def test_login_form_empty_username(self):
        form = LoginForm(data={
            'username': '',
            'password': 'test12345678'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_login_form_empty_password(self):
        form = LoginForm(data={
            'username': 'testuser',
            'password': ''
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_login_form_short_username(self):
        form = LoginForm(data={
            'username': 'ab',
            'password': 'test12345678'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_login_form_username_strip(self):
        form = LoginForm(data={
            'username': '  testuser  ',
            'password': 'test12345678'
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'testuser')

    def test_login_form_remember_me_optional(self):
        form = LoginForm(data={
            'username': 'testuser',
            'password': 'test12345678',
            'remember_me': True
        })
        self.assertTrue(form.is_valid())
        self.assertTrue(form.cleaned_data['remember_me'])

    def test_login_form_remember_me_default_false(self):
        form = LoginForm(data={
            'username': 'testuser',
            'password': 'test12345678'
        })
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data.get('remember_me', False))