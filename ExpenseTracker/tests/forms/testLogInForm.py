from django import forms
from django.test import TestCase
from ExpenseTracker.forms import LogInForm

class LoginFormTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.input = {
            'username': 'bob123',
            'password': 'Password12'
        }
        self.form = LogInForm(data=self.input)

    def testFormContainsCorrectFields(self):
        self.assertIn('username', self.form.fields)
        self.assertIn('password', self.form.fields)
        passwordField = self.form.fields['password']
        #checking if password is using the password widget
        self.assertTrue(isinstance(passwordField.widget, forms.PasswordInput)) 

    def testFormAcceptsValidInput(self):
        self.assertTrue(self.form.is_valid())

    def testFormAcceptsIncorrectUsername(self):
        self.input['username'] = 'random'
        self.assertTrue(LogInForm(data=self.input).is_valid())

    #With incorrect password form should still be deemed valid - not giving hints as to when stuff is wrong
    def testFormAcceptsIncorrectPassword(self):
        self.input['password'] = 'blah'
        self.assertTrue(LogInForm(data=self.input).is_valid())