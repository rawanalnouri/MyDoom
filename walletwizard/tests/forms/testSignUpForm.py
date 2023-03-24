'''Unit tests of sign up form.'''
from django import forms
from django.test import TestCase
from walletwizard.forms import SignUpForm
from django.urls import reverse

class SignUpFormTest(TestCase):
    '''Unit tests of sign up form.'''
    
    def setUp(self):
        self.input = {
            "firstName": "John",
            "lastName": "Doe",
            'username': 'testuser',
            "email": "johndoe@email.org",
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
        self.input['email'] = 'invalidEmail'
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testEmailCannotBeEmpty(self):
        self.input['email'] = ''
        self.assertFalse(SignUpForm(data=self.input).is_valid())

    def testEmailHasToBeUnique(self):
        self.client.post(reverse('signUp'), self.input)
        # Change other unique field so should fail at fact email not unique
        self.input['username'] = "9john" 
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
        # Change other unique field so should fail at fact username not unique
        self.input['email'] = "john@email.com"
        self.assertFalse(SignUpForm(data=self.input).is_valid())
        