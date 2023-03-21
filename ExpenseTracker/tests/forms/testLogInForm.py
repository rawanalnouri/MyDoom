''' Tests for form handling user login'''

from django import forms
from django.test import TestCase
from ExpenseTracker.forms import LogInForm

class LoginFormTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    # Create dictionary of input data for the form, and a form instance is created with that data.
    def setUp(self):
        self.input = {
            'username': 'bob123',
            'password': 'Password12'
        }
        self.form = LogInForm(data=self.input)

    # This checks that the form contains the correct fields, specifically the username and password fields
    def testFormContainsCorrectFields(self):
        self.assertIn('username', self.form.fields)
        self.assertIn('password', self.form.fields)
        passwordField = self.form.fields['password']
        #checking if password is using the password widget
        self.assertTrue(isinstance(passwordField.widget, forms.PasswordInput)) 

    # This tests that the form is valid when given the correct input data.
    def testFormAcceptsValidInput(self):
        self.assertTrue(self.form.is_valid())

    '''
    This tests that the form is still valid when given an incorrect username 
    because the form is not supposed to give hints as to whether the username or password is incorrect
    '''
    def testFormAcceptsIncorrectUsername(self):
        self.input['username'] = 'random'
        self.assertTrue(LogInForm(data=self.input).is_valid())

    # With incorrect password form should still be deemed valid - not giving hints as to when stuff is wrong
    def testFormAcceptsIncorrectPassword(self):
        self.input['password'] = 'blah'
        self.assertTrue(LogInForm(data=self.input).is_valid())
        