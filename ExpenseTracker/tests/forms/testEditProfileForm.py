from django import forms
from django.test import TestCase
from ExpenseTracker.forms import EditProfile
from ExpenseTracker.models import *


class EditProfileTestCase(TestCase):

    fixtures = [
        'ExpenseTracker/tests/fixtures/defualt_user.json'
    ]

    def setUp(self):
        self.input = {
            "firstName": "Jane",
            "lastName": "Doe",
            "username": "janedoe",
            "email": "janedoe@example.org",
        }

    def testFormHasNecessaryFields(self):
        form = EditProfile()
        self.assertIn('firstName', form.fields)
        self.assertIn('lastName', form.fields)
        self.assertIn('userName', form.fields)
        self.assertIn('email', form.fields)
        self.assertTrue(self.form.fields['email'], forms.EmailField)

    def testValidUserForm(self):
        form = EditProfile(data=self.form_input)
        self.assertTrue(form.is_valid())

    def testFormUsesModelValidation(self):
        self.form_input['username'] = 'badusername'
        form = EditProfile(data=self.form_input)
        self.assertFalse(form.is_valid())

    def testFormSavesCorrectly(self):
        user = User.objects.get(username='johndoe')
        form = EditProfile(instance=user, data=self.form_input)
        before_count = User.objects.count()
        form.save()
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(user.username, 'janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
