"""Tests for sign up view."""
from walletwizard.models import User 
from walletwizard.forms import SignUpForm
from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from walletwizard.tests.testHelpers import LogInTester

class SignUpViewTest(TestCase, LogInTester):
    """Tests for sign up view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.url = reverse('signUp')
        self.input = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'username': 'jane123',
            'email': 'janedoe@test.org',
            'newPassword': "Password123",
            'passwordConfirmation': "Password123"
        }
        self.form = SignUpForm(data = self.input)

    def testUrl(self):
        self.assertEqual('/signUp/', self.url)

    def testGetSignUpIfUserNotAuthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signUp.html')
        signUpForm = response.context['form']
        self.assertTrue(isinstance(signUpForm,SignUpForm))

    def testRedirectToHomeIfUserAuthenticated(self):
        user = User.objects.get(id=1)
        self.client.force_login(user)
        response = self.client.get(self.url)
        userHomePage = reverse('home')
        self.assertTemplateUsed('home.html')
        self.assertRedirects(response, userHomePage, status_code=302, target_status_code=200)


    def testUnsuccessfulSignUpWithInvalidEmail(self):
        self.input['email'] = 'email!'
        response = self.client.post(self.url, self.input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'signUp.html')
        form = response.context['form']
        self.assertTrue(isinstance(form,SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertIn('email', form.errors)
        self.assertFalse(self.isUserLoggedIn())

    def testUnsuccessfulSignUpWithEmptyFields(self):
        self.input['firstName'] = ''
        self.input['lastName'] = ''
        self.input['username'] = ''
        self.input['email'] = ''
        self.input['newPassword'] = ''
        self.input['passwordConfirmation'] = ''
        response = self.client.post(self.url, self.input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'signUp.html')
        form = response.context['form']
        self.assertTrue(isinstance(form,SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertIn('firstName', form.errors)
        self.assertIn('lastName', form.errors)
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('newPassword', form.errors)
        self.assertIn('passwordConfirmation', form.errors)
        self.assertFalse(self.isUserLoggedIn())

    def testUnsuccessfulSignUpDoesNotCreateNewUser(self):
        self.input['email'] = 'email!'
        totalUsersBefore = User.objects.count()
        self.client.post(self.url, self.input)
        totalUsersAfter = User.objects.count()
        self.assertEqual(totalUsersBefore, totalUsersAfter)

    def testSuccessfulSignUpAndRedirect(self):
        response = self.client.post(self.url, self.input, follow=True)
        newSignedUpUser = User.objects.get(email='janedoe@test.org')
        self.assertEqual(newSignedUpUser.firstName, 'Jane')
        self.assertEqual(newSignedUpUser.lastName,'Doe')
        self.assertTrue(check_password('Password123',newSignedUpUser.password))
        self.assertTrue(self.isUserLoggedIn())
        redirectUrl = reverse('home')
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "home.html")
    
    def testSuccessfulSignUpCreatesNewUser(self):
        totalUsersBefore = User.objects.count()
        self.client.post(self.url, self.input, follow=True)
        totalUsersAfter = User.objects.count()
        self.assertEqual(totalUsersBefore+1, totalUsersAfter)

    def testSignUpProhibitedWhenLoggedIn(self):
        user = User.objects.get(id=1)
        self.client.force_login(user)
        response = self.client.get(reverse('signUp'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('home.html')