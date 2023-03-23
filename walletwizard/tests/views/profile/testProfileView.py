"""Tests for profile view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User
from walletwizard.tests.testHelpers import reverse_with_next

class ProfileViewTest(TestCase):
    """Tests for profile view."""

    fixtures = [
        'walletwizard/tests/fixtures/defaultObjects.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.client.force_login(self.user)
        self.url = reverse('profile')

    def testProfileUrl(self):
        self.assertEqual(self.url, '/profile/')

    def testGetProfile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response,self.user.username)

    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')