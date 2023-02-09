from django import forms
from django.test import TestCase
from ExpenseTracker.forms import SignUpForm
from ExpenseTracker.models import User

class SignUpFormTest(TestCase):
    def setUp(self):
        self.input = {
            "first_name": "Bob",
            "last_name": "White",
            'username': 'bob123',
            "email": "bobwhite@email.org",
            "new_password": "Password123",
            "password_confirmation": "Password123"
        }
        self.form = SignUpForm(data=self.input)

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

    def testValidSignUp(self):
        self.assertTrue(self.form.is_valid())

    def testBothPasswordsAreEqual(self):
        self.input['password_confirmation'] = 'WrongPassword1234'
        form = SignUpForm(data = self.input)
        self.assertFalse(form.is_valid())

    def testFormDisallowsEmailWithoutAtSymbol(self):
        self.input['email'] = 'email'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testEmailCannotBeEmpty(self):
        self.input['email'] = ''
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testFormDisallowsPasswordsOfLengthLessThan8(self):
        self.input['new_password'] = 'test'
        self.input['password_confirmation'] = 'test'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testFromRejectsWhenPasswordsAreDifferent(self):
        self.input['new_password'] = 'Password123'
        self.input['password_confirmation'] = 'Password1234'
        self.assertFalse(SignUpForm(data=self.input).is_valid())


    # def testPasswordNeedsAnUpperCase(self):

    # def testPasswordNeedsANumber(self):

    # def testUsernameHasToBeUnique(self):