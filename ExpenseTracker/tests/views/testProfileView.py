from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.forms import EditProfile
from ExpenseTracker.models import *

#tests for the profile view

class ProfileViewTest(TestCase):

    fixtures = [
        'ExpenseTracker/tests/fixtures/defaultObjects.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='bob123')
        self.client.force_login(self.user)

        self.url = reverse('profile')
        self.formInput = {
            'firstName': 'John2',
            'lastName': 'Doe2',
            'username': 'johndoe2',
            'email': 'johndoe2@example.org',
        }

    def testProfileUrl(self):
        self.assertEqual(self.url, '/profile/')

    def testGetProfile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response,self.user.username)

    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')