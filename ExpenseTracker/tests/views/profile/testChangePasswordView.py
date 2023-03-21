"""Tests of the change password view."""
from django.test import TestCase
from ExpenseTracker.models import User
from django.urls import reverse
from ExpenseTracker.tests.testHelpers import reverse_with_next

class ChangeProfileViewTest(TestCase):
    """Tests of the change password view."""

    fixtures = [
        'ExpenseTracker/tests/fixtures/defaultObjects.json'
    ]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.url = reverse('changePassword')
        self.client.force_login(self.user)
        self.input = {
            'user': self.user,
            'old_password': "Password123",
            'new_password1': "Password123!",
            'new_password2': "Password123!",
        }

    def testRedirectsToHomeOnSuccess(self):
        response = self.client.post(self.url, self.input)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def testDisplaysErrorsOnFailure(self):
        self.input['old_password'] = ''
        response = self.client.post(self.url, self.input)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Please correct the errors below.')
        self.assertContains(response, 'This field is required.')

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')