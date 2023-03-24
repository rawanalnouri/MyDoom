"""Tests of the change password view."""
from django.test import TestCase
from walletwizard.models import User
from django.urls import reverse
from walletwizard.forms import PasswordChangeForm
from walletwizard.tests.testHelpers import reverse_with_next
from django.contrib.auth.hashers import check_password

class ChangeProfileViewTest(TestCase):
    """Tests of the change password view."""

    fixtures = [
        'walletwizard/tests/fixtures/defaultObjects.json'
    ]

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.url = reverse('changePassword')
        self.client.force_login(self.user)
        self.input = {
            'user': self.user,
            'old_password': "Password123",
            'new_password1': "NewPassword123",
            'new_password2': "NewPassword123",
        }

    def testChangePasswordUrl(self):
        self.assertEqual(self.url, '/changePassword/')

    def testRedirectsToHomeOnSuccess(self):
        response = self.client.post(self.url, self.input, follow=True)
        responseUrl = reverse('home')
        self.assertRedirects(response, responseUrl, status_code=302, target_status_code=200)
        self.user.refresh_from_db()
        isPasswordCorrect = check_password('NewPassword123', self.user.password)
        self.assertTrue(isPasswordCorrect)

    def testChangePasswordIsUnsuccesfulIfOldPasswordIsBlank(self):
        self.input['old_password'] = ''
        response = self.client.post(self.url, self.input)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Please correct the errors below.')
        self.assertContains(response, 'This field is required.')
    
    def testChangePasswordIsUnsuccesfulWithIncorrectOldPassword(self):
        self.input['old_password'] = 'WrongPassword123'
        response = self.client.post(self.url, self.input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'changePassword.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangeForm))
        self.user.refresh_from_db()
        isPasswordCorrect = check_password('Password123', self.user.password)
        self.assertTrue(isPasswordCorrect)

    def testChangePasswordUnsuccesfulIfPasswordConfirmationDoesNotMatch(self):
        self.input['new_password2'] = 'WrongPassword123'
        response = self.client.post(self.url, self.input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'changePassword.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, PasswordChangeForm))
        self.user.refresh_from_db()
        isPasswordCorrect = check_password('Password123', self.user.password)
        self.assertTrue(isPasswordCorrect)

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')