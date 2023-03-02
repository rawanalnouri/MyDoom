from ExpenseTracker.models import User 
from ExpenseTracker.forms import LogInForm
from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib import messages
from ExpenseTracker.tests.helpers import LogInTester


class TestLoginView(TestCase, LogInTester):
    fixtures = ['ExpenseTracker/tests/fixtures/defualt_objects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.input = {
            'username': 'bob123',
            'password': 'Password123'
        }
        self.url = reverse('logIn')

    def testLogInUrl(self):
        self.assertEqual(self.url, '/logIn/')

    def testGetLogIn(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logIn.html')
        loginForm = response.context['form']
        self.assertTrue(isinstance(loginForm, LogInForm))
        self.assertFalse(loginForm.is_bound) 
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages),0)

    def testUnsuccessfulLogin(self):
        self.input['password'] = ''
        response = self.client.post(self.url, self.input)
        self.assertFalse(self.isUserLoggedIn())
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        #Check for error message
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages),1)
        self.assertEqual(listOfMessages[0].level, messages.ERROR)

    def testSuccessfulLogInAndRedirect(self):
        response = self.client.post(self.url, self.input, follow=True)
        self.assertTrue(self.isUserLoggedIn())
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        #No Error Messages recieved
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages), 0)




