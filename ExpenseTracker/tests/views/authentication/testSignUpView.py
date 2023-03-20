# Tests for the sign up view

from ExpenseTracker.models import User 
from ExpenseTracker.forms import SignUpForm
from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from ExpenseTracker.tests.testHelpers import LogInTester

class SignUpViewTest(TestCase, LogInTester):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

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

    #  This test checks whether the URL for the sign-up view is correct. 
    def testUrl(self):
        self.assertEqual('/signUp/', self.url)

    #  This test checks that a user who is not logged in can  access the sign-up page successfully. 
    def testGetSignUpIfUserNotAuthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signUp.html')
        signUpForm = response.context['form']
        self.assertTrue(isinstance(signUpForm,SignUpForm))

    # This test checks if a user is logged in, they will be taken to home page if they try to access the sign-up page.
    def testRedirectToHomeIfUserAuthenticated(self):
        user = User.objects.get(id=1)
        self.client.force_login(user)
        response = self.client.get(self.url)
        userHomePage = reverse('home')
        self.assertRedirects(response, userHomePage, status_code=302, target_status_code=200)

    # This test checks that an unsuccessful sign-up attempt will not create a new user. 
    def testUnsuccessfulSignUp(self):
        self.input['email'] = 'email!'
        totalUsersBefore = User.objects.count()
        response = self.client.post(self.url, self.input)
        totalUsersAfter = User.objects.count()
        self.assertEqual(totalUsersBefore, totalUsersAfter)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'signUp.html')
        form = response.context['form']
        self.assertTrue(isinstance(form,SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self.isUserLoggedIn())

    # This test checks that a successful sign-up attempt will create a new user and redirect them to the home page. 
    def testSuccessfulSignUpAndRedirect(self):
        totalUsersBefore = User.objects.count()
        response = self.client.post(self.url, self.input, follow=True)
        totalUsersAfter = User.objects.count()
        self.assertEqual(totalUsersBefore+1, totalUsersAfter)

        newSignedUpUser = User.objects.get(email='janedoe@test.org')
        self.assertEqual(newSignedUpUser.firstName, 'Jane')
        self.assertEqual(newSignedUpUser.lastName,'Doe')
        self.assertTrue(check_password('Password123',newSignedUpUser.password))
        self.assertTrue(self.isUserLoggedIn())

        userHomePage = reverse('home')
        self.assertRedirects(response, userHomePage, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "home.html")