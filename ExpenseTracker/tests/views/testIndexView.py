from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User
class IndexViewTest(TestCase):

    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

    def testGetIndexViewWhenNotLoggedIn(self):
        self.client.logout()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def testRedirectsToHomeIfLoggedIn(self):
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, reverse('home'))