# Tests for the index view

from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User

class IndexViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

    # This test verifies that the index view is accessible and returns an HTTP status code of 200 when the user is not logged in.
    def testGetIndexViewWhenNotLoggedIn(self):
        self.client.logout()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    # This test verifies that when a user is already logged in and tries to access the index view, they are redirected to the home view. 
    def testRedirectsToHomeIfLoggedIn(self):
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, reverse('home'))