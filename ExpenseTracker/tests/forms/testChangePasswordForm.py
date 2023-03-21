''' Tests for form handling user changing their password'''

from django import forms
from django.test import TestCase
from ExpenseTracker.forms import ChangePasswordForm
from ExpenseTracker.models import *

class ChangePasswordFormTest(TestCase):
    fixtures = [
        'ExpenseTracker/tests/fixtures/defaultObjects.json'
    ]
    
    # Retrieves user from the database and creates dictionary of input data for the form
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.input = {
            'old_password': "Password123",
            'new_password1': "Password123!",
            'new_password2': "Password123!",
        }
 
    # This test checks that the form has the necessary fields
    def testFormHasNecessaryFields(self):
        form = ChangePasswordForm(user=self.user)
        self.assertIn('old_password', form.fields)
        self.assertIn('new_password1', form.fields)
        self.assertIn('new_password2', form.fields)
 
    # This test checks if the form is valid when given valid input data
    def testValidUserForm(self):
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertTrue(form.is_valid())
    
    # This test checks if the form uses is_invalid when the new passwords don't match
    def testFormUsesIsInvalidWhenNewPasswordsDontMatch(self):
        self.input['new_password2'] = 'Password123!!'
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertFalse(form.is_valid())

    # This test checks if the form uses model validation to ensure that the new password is not too short
    def testFormUsesModelValidation(self):
        # Ensures password cannot be short
        self.input['new_password1'] = 'P'
        self.input['new_password2'] = 'P'
        form = ChangePasswordForm(user=self.user, data=self.input)
        self.assertFalse(form.is_valid())

    # This test checks if the form saves the new password correctly
    def testFormSavesCorrectly(self):
        passwordBefore = self.user.password
        form = ChangePasswordForm(user=self.user, data=self.input)
        form.is_valid()
        form.save()
        passwordAfter = self.user.password
        self.assertNotEqual(passwordBefore, passwordAfter)
        