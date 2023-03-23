"""Tests for edit profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from walletwizard.forms import EditProfileForm
from walletwizard.models import User
from walletwizard.tests.testHelpers import reverse_with_next

class EditProfileViewTest(TestCase):
    """Tests for edit profile view."""

    fixtures = [
        'walletwizard/tests/fixtures/defaultObjects.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.client.force_login(self.user)
        self.url = reverse('editProfile')
        self.formInput = {
            'firstName': 'John2',
            'lastName': 'Doe2',
            'username': 'johndoe2',
            'email': 'johndoe2@example.org',
        }

    def testEditProfileUrl(self):
        self.assertEqual(self.url, '/editProfile/')

    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')

    def testGetEditProfile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editProfile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))
    
    def testUnsuccesfulProfileUpdate(self):
        self.formInput['username'] = 'b'
        self.formInput['email'] = 'invalidEmail'
        response = self.client.post(self.url, self.formInput)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.is_bound)
        self.assertTemplateUsed(response, 'editProfile.html')
        # check user does not update
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.firstName, 'john')
        self.assertEqual(self.user.lastName, 'doe')
        self.assertEqual(self.user.email, 'johndoe@email.com')
        # check errors
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
    
    def testSuccesfulProfileUpdate(self):
        response = self.client.post(self.url, self.formInput, follow=True)
        responseUrl = reverse('profile')
        self.assertRedirects(response, responseUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile.html')
        # check user updates
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe2')
        self.assertEqual(self.user.firstName, 'John2')
        self.assertEqual(self.user.lastName, 'Doe2')
        self.assertEqual(self.user.email, 'johndoe2@example.org')
        # check messages
        messagesList = list(response.context['messages'])
        self.assertEqual(len(messagesList), 1)
        self.assertEqual(str(messagesList[0]), 'Your profile has been updated successfully.')
        self.assertEqual(messagesList[0].level, messages.SUCCESS)

    def testSuccesfulProfileUpdateDoesNotIncreaseNumberOfUsers(self):
        beforeCount = User.objects.count()
        self.client.post(self.url, self.formInput, follow=True)
        afterCount = User.objects.count()
        self.assertEqual(afterCount, beforeCount)