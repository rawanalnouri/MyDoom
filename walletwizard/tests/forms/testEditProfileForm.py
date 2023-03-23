'''Unit tests of the edit profile form.'''
from django import forms
from django.test import TestCase
from walletwizard.forms import EditProfileForm
from walletwizard.models import User

class EditProfileFormTestCase(TestCase):
    '''Unit tests of the edit profile form.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']
    
    def setUp(self):
        self.input = {
            "firstName": "Jane",
            "lastName": "Doe",
            "username": "janedoe",
            "email": "janedoe@example.org",
        }

    def testFormHasNecessaryFieldsAndWidgets(self):
        form = EditProfileForm()
        self.assertIn('firstName', form.fields)
        self.assertIn('lastName', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertTrue(form.fields['email'], forms.EmailField)

    def testFormValidation(self):
        form = EditProfileForm(data=self.input)
        self.assertTrue(form.is_valid())

    def testFormDoesNotAcceptUsernameThatAlreadyExists(self):
        self.input['username'] = 'testuser'
        form = EditProfileForm(data=self.input)
        self.assertFalse(form.is_valid())
    
    def testFormValidationMissingFields(self):
        self.input['firstName'] = ''
        self.input['lastName'] = ''
        self.input['username'] = ''
        self.input['email'] = ''
        form = EditProfileForm(data=self.input)
        self.assertFalse(form.is_valid())

    def testFormUsesModelValidationForUsername(self):
        self.input['username'] = 'b'
        form = EditProfileForm(data=self.input)
        self.assertFalse(form.is_valid())
    
    def testFormUsesModelValidationForEmail(self):
        self.input['email'] = 'invalidEmail'
        form = EditProfileForm(data=self.input)
        self.assertFalse(form.is_valid())

    def testFormSavesCorrectly(self):
        user = User.objects.get(username='testuser')
        form = EditProfileForm(instance=user, data=self.input)
        beforeCount = User.objects.count()
        form.save()
        afterCount = User.objects.count()
        self.assertEqual(afterCount, beforeCount)
        self.assertEqual(user.username, 'janedoe')
        self.assertEqual(user.firstName, 'Jane')
        self.assertEqual(user.lastName, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')