from ExpenseTracker.models import User 
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib import messages
from ExpenseTracker.tests.helpers import LogInTester

#tests for the log out view

class TestLogOut(TestCase, LogInTester):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.url = reverse('logOut')
        self.user = User.objects.get(id=1)

    # This test checks if the URL for the log out view is correct.
    def testUrl(self):
        self.assertEqual(self.url,'/logOut/')

    # This test logs in a user, calls the log out view, and checks if 
    # the user has been successfully logged out and redirected to the index page.
    def testLogOutAndRedirect(self):
        self.client.login(username='bob123', password='Password123')
        self.assertTrue(self.isUserLoggedIn())

        #Get log out view and check if user has been succesfully logged out
        response = self.client.get(self.url, follow=True)
        response_url = reverse('index')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertFalse(self.isUserLoggedIn())

    # This test checks if the log out button is not shown on the page when 
    # the user is not logged in.
    def testLogOutNotShownWhenNotLoggedIn(self):
        response = self.client.get('')
        self.assertNotContains(response, 'logOut')

    # This test logs in a user and checks if the log out button is shown
    # on the home page.
    def testLogOutShownWhenLoggedIn(self):
        self.client.login(username='bob123', password='Password123')
        response = self.client.get('/home/')
        self.assertContains(response, 'logOut')

    # This test checks if the user is redirected to the login page when the user is not 
    # logged in and tries to access the log out view.
    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('logOut'))
        self.assertRedirects(response, reverse('logIn'))
