'''Unit tests of the log in form.'''
from django import forms
from django.test import TestCase
from walletwizard.forms import LogInForm
from walletwizard.models import User

class LoginFormTest(TestCase):
    '''Unit tests of the log in form.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.input = {
            'username': 'testuser',
            'password': 'Password123'
        }
        self.form = LogInForm(data=self.input)

    def testFormAcceptsValidInput(self):
        self.assertTrue(self.form.is_valid())
        
    def testFormContainsCorrectFields(self):
        self.assertIn('username', self.form.fields)
        self.assertIn('password', self.form.fields)
        passwordField = self.form.fields['password']
        self.assertTrue(isinstance(passwordField.widget, forms.PasswordInput)) 

    def testFormDoesNotAcceptBlankUsername(self):
        self.input['username'] = ''
        form = LogInForm(data=self.input)
        self.assertFalse(form.is_valid())
        user = form.getUser()
        self.assertEqual(user, None)

    def testFormDoesNotAcceptBlankPassword(self):
        self.input['password'] = ''
        form = LogInForm(data=self.input)
        self.assertFalse(form.is_valid())
        user = form.getUser()
        self.assertEqual(user, None)

    def testFormAcceptsIncorrectUsername(self):
        self.input['username'] = 'blah'
        form = LogInForm(data=self.input)
        self.assertTrue(form.is_valid())
    
    def testFormAcceptsIncorrectPassword(self):
        self.input['password'] = 'blah'
        form = LogInForm(data=self.input)
        self.assertTrue(form.is_valid())

    def testCanAuthenticateValidUser(self):
        fixture = self.user
        form = LogInForm(data=self.input)
        user = form.getUser()
        self.assertEqual(user, fixture)

    def testInvalidCredentialsDoNotAuthenticate(self):
        self.input['password'] = 'WrongPassword123'
        form = LogInForm(data=self.input)
        user = form.getUser()
        self.assertEqual(user, None)