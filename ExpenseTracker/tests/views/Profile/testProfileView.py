# Tests for the profile view

from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.forms import EditProfile
from ExpenseTracker.models import *

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

    #  This test checks that the url attribute of the ProfileView class is set to '/profile/'.
    def testProfileUrl(self):
        self.assertEqual(self.url, '/profile/')

    # This test checks that a logged-in user can access their own profile page. 
    def testGetProfile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response,self.user.username)

    # This test checks that a user who is not logged in is taken to the login page when accessing the profile page. 
    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')