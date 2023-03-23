'''Unit tests of the change password form.'''
from django.test import TestCase
from django import forms
from walletwizard.forms import ChangePasswordForm
from walletwizard.models import User

class ChangePasswordFormTest(TestCase):
    '''Unit tests of the change password form.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']
    
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.input = {
            'old_password': "Password123",
            'new_password1': "Password123!",
            'new_password2': "Password123!",
        }

    def testFormHasNecessaryFieldsAndWidgets(self):
        form = ChangePasswordForm(user=self.user)
        self.assertIn('old_password', form.fields)
        self.assertIn('new_password1', form.fields)
        self.assertIn('new_password2', form.fields) 
        self.assertTrue(form.fields['old_password'].widget, forms.PasswordInput)
        self.assertTrue(form.fields['new_password1'].widget, forms.PasswordInput)
        self.assertTrue(form.fields['new_password2'].widget, forms.PasswordInput)
 
    def testFormAcceptsValidInput(self):
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertTrue(form.is_valid())
    
    def testFormIsInvalidIfNewPasswordIsNotIdenticalToPasswordConfirmation(self):
        self.input['new_password2'] = 'WrongPassword123!'
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertFalse(form.is_valid())

    def testPasswordMustContainLowercaseCharacter(self):
        self.input['new_password1'] = 'PASSWORD123'
        self.input['new_password2'] = 'PASSWORD123'
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertFalse(form.is_valid())

    def testPasswordMustContainAtLeastThreeCharacters(self):
        self.input['new_password1'] = 'P'
        self.input['new_password2'] = 'P'
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertFalse(form.is_valid())

    def testFormSavesCorrectly(self):
        passwordBefore = self.user.password
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertTrue(form.is_valid())
        form.save()
        passwordAfter = self.user.password
        self.assertNotEqual(passwordBefore, passwordAfter)