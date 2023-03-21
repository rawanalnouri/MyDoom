''' Tests for form handling user sign up'''
from django import forms
from django.test import TestCase
from walletwizard.forms import SignUpForm
from walletwizard.models import User
from django.urls import reverse

class SignUpFormTest(TestCase):
    
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
    
    def testValidSignUp(self):
        self.assertTrue(self.form.is_valid())

    def testBothPasswordsAreEqual(self):
        self.input['passwordConfirmation'] = 'WrongPassword1234'
        form = SignUpForm(data = self.input)
        self.assertFalse(form.is_valid())

    def testFormDisallowsEmailWithoutAtSymbol(self):
        self.input['email'] = 'email'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testEmailCannotBeEmpty(self):
        self.input['email'] = ''
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testEmailHasToBeUnique(self):
        self.client.post(reverse('signUp'), self.input)
        # Change other unique field so should fail at fact email not unique
        self.input['username'] = "9bob" 
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testFormDisallowsPasswordsOfLengthLessThan8(self):
        self.input['newPassword'] = 'test'
        self.input['passwordConfirmation'] = 'test'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testFromRejectsWhenPasswordsAreDifferent(self):
        self.input['new_password'] = 'Password123'
        self.input['passwordConfirmation'] = 'Password1234'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testPasswordNeedsAnUpperCase(self):
        self.input['newPassword'] = 'password123'
        self.input['passwordConfirmation'] = 'password1234'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testPasswordNeedsANumber(self):
        self.input['newPassword'] = 'password'
        self.input['passwordConfirmation'] = 'password'
        self.assertFalse(SignUpForm(data=self.input).is_valid())
 
    def testUsernameHasToBeUnique(self):
        self.client.post(reverse('signUp'), self.input)
        #change other unique field so should fail at fact username not unique
        self.input['email'] = "bob@email.com"
        self.assertFalse(SignUpForm(data=self.input).is_valid())
        