from ExpenseTracker.models import User 
from ExpenseTracker.forms import SignUpForm
from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from ExpenseTracker.tests.helpers import LogInTester

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


    def testUrl(self):
        self.assertEqual('/signUp/', self.url)

    def testGetSignUpIfUserNotAuthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signUp.html')
        signUpForm = response.context['form']
        self.assertTrue(isinstance(signUpForm,SignUpForm))

    def testRedirectToHomeIfUserAuthenticated(self):
        # User should be taken to the home page if logged in
        user = User.objects.get(id=1)
        self.client.force_login(user)
        response = self.client.get(self.url)
        userHomePage = reverse('home')
        self.assertRedirects(response, userHomePage, status_code=302, target_status_code=200)

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

    def testSuccessfulSignUpAndRedirect(self):
        totalUsersBefore = User.objects.count()
        response = self.client.post(self.url, self.input, follow=True)
        totalUsersAfter = User.objects.count()
        self.assertEqual(totalUsersBefore+1, totalUsersAfter)

        #Check data saved correctly
        newSignedUpUser = User.objects.get(email='janedoe@test.org')
        self.assertEqual(newSignedUpUser.firstName, 'Jane')
        self.assertEqual(newSignedUpUser.lastName,'Doe')
        self.assertTrue(check_password('Password123',newSignedUpUser.password))
        self.assertTrue(self.isUserLoggedIn())

        #Check Redirects
        userHomePage = reverse('home')
        self.assertRedirects(response, userHomePage, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "home.html")