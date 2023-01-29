from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User

class HomeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def testHomeViewUsesCorrectTemplate(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def testHomeViewRedirectsToLoginIfNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/logIn/?next=' + reverse('home'))