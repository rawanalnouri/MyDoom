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

    #  This test checks that the url attribute of the ProfileView class is set to '/profile/'.
    def testProfileUrl(self):
        self.assertEqual(self.url, '/profile/')


    # This test checks that a logged-in user can access their own profile page. 
    # 
    # It sends a GET request to the profile URL and checks that the response has a status code of 200, 
    # uses the correct template (profile.html), and contains the logged-in user's username.
    def testGetProfile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response,self.user.username)

    # This test checks that a user who is not logged in is redirected to the login 
    # page when they try to access the profile page. 
    # 
    # It logs the user out, sends a GET request to the profile URL, and checks 
    # that the response has a status code of 302 (redirect), that it redirects 
    # to the login page, and that the login page template is used.
    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')