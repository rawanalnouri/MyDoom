from django import forms
from django.test import TestCase
from ExpenseTracker.forms import ChangePasswordForm
from ExpenseTracker.models import *
from django.urls import reverse


class ChangeProfileViewTest(TestCase):

    fixtures = [
        'ExpenseTracker/tests/fixtures/defaultObjects.json'
    ]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.input = {
            'user': self.user,
            'old_password': "Password123",
            'new_password1': "Password123!",
            'new_password2': "Password123!",
        }


    def testRedirectsToHomeOnSuccess(self):
        oldPassword = self.user.password
        response = self.client.post(reverse('changePassword'), self.input)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def testDisplaysErrorsOnFailure(self):
        self.input['old_password'] = ''
        response = self.client.post(reverse('changePassword'), self.input)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Please correct the errors below.')
        self.assertContains(response, 'This field is required.')


    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('changePassword'))
        self.assertRedirects(response, reverse('logIn'))


