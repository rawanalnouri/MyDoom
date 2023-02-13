from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User

class HomeViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defualt_objects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

    def testHomeViewUsesCorrectTemplate(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def testHomeViewRedirectsToLoginIfNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/logIn/?next=' + reverse('home'))