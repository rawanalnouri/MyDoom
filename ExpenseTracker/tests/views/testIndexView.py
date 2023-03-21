"""Tests of the index view."""

from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User

class IndexViewTest(TestCase):
    """Tests of the index view."""

    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.url = reverse('index')
        self.user = User.objects.get(id=1)
    
    def testIndexUrl(self):
        self.assertEqual(self.url, '/')

    def testGetIndexViewWhenNotLoggedIn(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
 
    def testIndexRedirectsToHomeWhenLoggedIn(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, follow=True)
        redirectUrl = reverse('home')
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')