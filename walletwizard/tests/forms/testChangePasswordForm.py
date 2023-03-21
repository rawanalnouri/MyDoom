''' Tests for form handling user changing their password'''

from django import forms
from django.test import TestCase
from walletwizard.forms import ChangePasswordForm
from walletwizard.models import *

class ChangePasswordFormTest(TestCase):
    fixtures = [
        'walletwizard/tests/fixtures/defaultObjects.json'
    ]
    
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.input = {
            'old_password': "Password123",
            'new_password1': "Password123!",
            'new_password2': "Password123!",
        }

    def testFormHasNecessaryFields(self):
        form = ChangePasswordForm(user=self.user)
        self.assertIn('old_password', form.fields)
        self.assertIn('new_password1', form.fields)
        self.assertIn('new_password2', form.fields)
 
    def testValidUserForm(self):
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertTrue(form.is_valid())
    
    def testFormUsesIsInvalidWhenNewPasswordsDontMatch(self):
        self.input['new_password2'] = 'Password123!!'
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertFalse(form.is_valid())

    def testFormUsesModelValidation(self):
        # Ensures password cannot be short
        self.input['new_password1'] = 'P'
        self.input['new_password2'] = 'P'
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertFalse(form.is_valid())

    def testFormSavesCorrectly(self):
        passwordBefore = self.user.password
        form = ChangePasswordForm(user=self.user, data=self.input)
        form.is_valid()
        form.save()
        passwordAfter = self.user.password
        self.assertNotEqual(passwordBefore, passwordAfter)
        