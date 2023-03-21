''' Tests for form handling user editing their profile'''

from django import forms
from django.test import TestCase
from walletwizard.forms import EditProfileForm
from walletwizard.models import *

class EditProfileFormTestCase(TestCase):
    fixtures = [
        'walletwizard/tests/fixtures/defaultObjects.json'
    ]
    
    def setUp(self):
        self.input = {
            "firstName": "Jane",
            "lastName": "Doe",
            "username": "janedoe",
            "email": "janedoe@example.org",
        }

    def testFormHasNecessaryFields(self):
        form = EditProfileForm()
        self.assertIn('firstName', form.fields)
        self.assertIn('lastName', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)
        self.assertTrue(form.fields['email'], forms.EmailField)

    def testValidUserForm(self):
        form = EditProfileForm(data=self.input)
        self.assertTrue(form.is_valid())

    def testFormUsesModelValidation(self):
        # Ensure you cannot use an existing username
        self.input['username'] = 'bob123'
        form = EditProfileForm(data=self.input)
        self.assertFalse(form.is_valid())

    def testFormSavesCorrectly(self):
        user = User.objects.get(username='bob123')
        form = EditProfileForm(instance=user, data=self.input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.username, 'janedoe')
        self.assertEqual(user.firstName, 'Jane')
        self.assertEqual(user.lastName, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        