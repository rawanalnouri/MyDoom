from ExpenseTracker.models import User 
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib import messages
from ExpenseTracker.tests.helpers import LogInTester

class TestLogOut(TestCase, LogInTester):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.url = reverse('logOut')
        self.user = User.objects.get(id=1)

    def testUrl(self):
        self.assertEqual(self.url,'/logOut/')

    def testLogOutAndRedirect(self):
        self.client.login(username='bob123', password='Password123')
        self.assertTrue(self.isUserLoggedIn())

        #Get log out view and check if user has been succesfully logged out
        response = self.client.get(self.url, follow=True)
        response_url = reverse('index')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertFalse(self.isUserLoggedIn())

    def testLogOutNotShownWhenNotLoggedIn(self):
        response = self.client.get('')
        self.assertNotContains(response, 'logOut')

    def testLogOutShownWhenLoggedIn(self):
        self.client.login(username='bob123', password='Password123')
        response = self.client.get('/home/')
        self.assertContains(response, 'logOut')

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('showUser', kwargs={'userId': self.user.id}))
        self.assertRedirects(response, reverse('logIn'))
