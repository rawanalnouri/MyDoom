"""Tests for log out view."""
from ExpenseTracker.models import User 
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.tests.testHelpers import LogInTester
from ExpenseTracker.tests.testHelpers import reverse_with_next

class LogOutViewTest(TestCase, LogInTester): 
    """Tests for log out view."""

    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.url = reverse('logOut')
        self.user = User.objects.get(id=1)

    def testUrl(self):
        self.assertEqual(self.url,'/logOut/')

    def testLogOutAndRedirect(self):
        self.client.login(username='bob123', password='Password123')
        self.assertTrue(self.isUserLoggedIn())
        response = self.client.get(self.url, follow=True)
        response_url = reverse('index')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertFalse(self.isUserLoggedIn())

    def testLogOutNotShownWhenNotLoggedIn(self):
        response = self.client.get('')
        self.assertNotContains(response, 'logOut')

    def testLogOutShownWhenLoggedIn(self):
        self.client.login(username='bob123', password='Password123')
        response = self.client.get('/home/')
        self.assertContains(response, 'logOut')

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')