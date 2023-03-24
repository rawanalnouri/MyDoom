"""Tests of the index view."""

from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User
from PersonalSpendingTracker.settings import REDIRECT_URL_WHEN_LOGGED_IN 

class IndexViewTest(TestCase):
    """Tests of the index view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

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
        redirectUrl = reverse(REDIRECT_URL_WHEN_LOGGED_IN)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')