from ExpenseTracker.models import User 
from ExpenseTracker.forms import SignUpForm
from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from ExpenseTracker.tests.helpers import LogInTester

class SignUpViewTest(TestCase, LogInTester):
    def setUp(self):
        self.url = reverse('signUp')
        self.input = {
            'first_name': 'Bob',
            'last_name': 'Doe',
            'username': 'bob123',
            'email': 'bobdoe@test.org',
            'new_password': "Password123",
            'password_confirmation': "Password123"
        }
        self.form = SignUpForm(data = self.input)


    def testUrl(self):
        self.assertEqual('/signUp/', self.url)

    def testValidSignUpForm(self):
        self.assertTrue(self.form.is_valid())

    def testGetSignUp(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signUp.html')
        signUpForm = response.context['form']
        self.assertTrue(isinstance(signUpForm,SignUpForm))

    def testFormHasCorrectFields(self):
        self.assertIn('first_name', self.form.fields)
        self.assertIn('last_name', self.form.fields)
        self.assertIn('username', self.form.fields)
        self.assertIn('email', self.form.fields)
        self.assertIn('new_password', self.form.fields)
        self.assertIn('password_confirmation', self.form.fields)
        self.assertTrue(self.form.fields['email'], forms.EmailField)
        self.assertTrue(self.form.fields['new_password'].widget, forms.PasswordInput)
        self.assertTrue(self.form.fields['password_confirmation'].widget, forms.PasswordInput)

    def testBothPasswordsAreEqual(self):
        self.input['password_confirmation'] = 'WrongPassword1234'
        form = SignUpForm(data = self.input)
        self.assertFalse(form.is_valid())

    def testModelValidation(self):
        self.input['email'] = 'email'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testUnsuccessfulSignUp(self):
        self.input['email'] = 'email!'
        totalUsersBefore = User.objects.count()
        response = self.client.post(self.url, self.input)
        totalUsersAfter = User.objects.count()
        self.assertEqual(totalUsersBefore, totalUsersAfter)
        self.assertFalse(self.isUserLoggedIn())

    def testSuccessfulSignUpAndRedirect(self):
        totalUsersBefore = User.objects.count()
        response = self.client.post(self.url, self.input, follow=True)
        totalUsersAfter = User.objects.count()
        self.assertEqual(totalUsersBefore+1, totalUsersAfter)

        #Check data saved correctly
        newSignedUpUser = User.objects.get(email='bobdoe@test.org')
        self.assertEqual(newSignedUpUser.first_name, 'Bob')
        self.assertEqual(newSignedUpUser.last_name,'Doe')
        self.assertTrue(check_password('Password123',newSignedUpUser.password))
        self.assertTrue(self.isUserLoggedIn())

        #Check Redirects
        user = auth.get_user(self.client)
        userHomePage = reverse('home')
        self.assertRedirects(response, userHomePage, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "home.html")


