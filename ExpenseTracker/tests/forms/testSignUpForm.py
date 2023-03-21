''' Tests for form handling user sign up'''

from django import forms
from django.test import TestCase
from ExpenseTracker.forms import SignUpForm
from ExpenseTracker.models import User
from django.urls import reverse

class SignUpFormTest(TestCase):
    # Initialises some data for the tests, including an input dictionary with user information and a SignUpForm instance with that data
    def setUp(self):
        self.input = {
            "firstName": "Bob",
            "lastName": "White",
            'username': 'bob123',
            "email": "bobwhite@email.org",
            "newPassword": "Password123",
            "passwordConfirmation": "Password123"
        }
        self.form = SignUpForm(data=self.input)

    # This checks that all the expected fields are present in the form
    def testFormHasCorrectFields(self):
        self.assertIn('firstName', self.form.fields)
        self.assertIn('lastName', self.form.fields)
        self.assertIn('username', self.form.fields)
        self.assertIn('email', self.form.fields)
        self.assertIn('newPassword', self.form.fields)
        self.assertIn('passwordConfirmation', self.form.fields)
        self.assertTrue(self.form.fields['email'], forms.EmailField)
        self.assertTrue(self.form.fields['newPassword'].widget, forms.PasswordInput)
        self.assertTrue(self.form.fields['passwordConfirmation'].widget, forms.PasswordInput)

    # This checks that the form is valid when all the fields are correctly filled out.
    def testValidSignUp(self):
        self.assertTrue(self.form.is_valid())

    # This checks that the form is invalid when the password confirmation does not match the original password
    def testBothPasswordsAreEqual(self):
        self.input['passwordConfirmation'] = 'WrongPassword1234'
        form = SignUpForm(data = self.input)
        self.assertFalse(form.is_valid())

    # This checks that the form is invalid when the email field does not contain an '@' symbol
    def testFormDisallowsEmailWithoutAtSymbol(self):
        self.input['email'] = 'email'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    # This checks that the form is invalid when the email field is empty
    def testEmailCannotBeEmpty(self):
        self.input['email'] = ''
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    # This checks that the form is invalid when the email field is not unique
    def testEmailHasToBeUnique(self):
        self.client.post(reverse('signUp'), self.input)
        # Change other unique field so should fail at fact email not unique
        self.input['username'] = "9bob" 
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    # This checks that the form is invalid when the password is less than 8 characters long
    def testFormDisallowsPasswordsOfLengthLessThan8(self):
        self.input['newPassword'] = 'test'
        self.input['passwordConfirmation'] = 'test'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    # This checks that the form is invalid when the two password fields do not match
    def testFromRejectsWhenPasswordsAreDifferent(self):
        self.input['new_password'] = 'Password123'
        self.input['passwordConfirmation'] = 'Password1234'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    # This checks that the form is invalid when the password does not contain an uppercase letter
    def testPasswordNeedsAnUpperCase(self):
        self.input['newPassword'] = 'password123'
        self.input['passwordConfirmation'] = 'password1234'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    # This checks that the form is invalid when the password does not contain a number
    def testPasswordNeedsANumber(self):
        self.input['newPassword'] = 'password'
        self.input['passwordConfirmation'] = 'password'
        self.assertFalse(SignUpForm(data=self.input).is_valid())
 
    # This checks that the form is invalid when the username field is not unique
    def testUsernameHasToBeUnique(self):
        self.client.post(reverse('signUp'), self.input)
        #change other unique field so should fail at fact username not unique
        self.input['email'] = "bob@email.com"
        self.assertFalse(SignUpForm(data=self.input).is_valid())
        