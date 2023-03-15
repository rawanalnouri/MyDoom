from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.forms import EditProfile
from ExpenseTracker.models import *

#tests for the edit profile view

class EditProfileViewTest(TestCase):

    fixtures = [
        'ExpenseTracker/tests/fixtures/defaultObjects.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='bob123')
        self.client.force_login(self.user)

        self.url = reverse('editProfile')
        self.formInput = {
            'firstName': 'John2',
            'lastName': 'Doe2',
            'username': 'johndoe2',
            'email': 'johndoe2@example.org',
        }

    # This test ensures that a user who is not logged in is redirected 
    # to the login page when they try to access the edit profile page.
    #  
    # It checks that the HTTP response status code is 302, 
    # which means a redirect occurred. 
    # It then checks that the response redirected to the login 
    # page and that the login page template is used.
    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')

    # This test checks that the edit profile page is displayed properly when the user is logged in. 
    # 
    # It verifies that the HTTP response status code is 200, 
    # indicating that the page loaded successfully.
    # It also ensures that the correct template is used and that 
    # the form context is of the correct type.
    def testGetSignUp(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editProfile.html')
        signUpForm = response.context['form']
        self.assertTrue(isinstance(signUpForm,EditProfile))

    # This test checks that an update to the user profile is unsuccessful if invalid data is submitted.
    # 
    #  It sets invalid data and submits the form. 
    # It verifies that the HTTP response status code is 200, 
    # indicating that the form submission was unsuccessful. 
    # It also ensures that the correct template is used, that the form
    # is bound and that the user object is not updated.
    def testUnsuccesfulProfileUpdate(self):
        self.formInput['username'] = "a{35}"
        before_count = User.objects.count()
        response = self.client.post(self.url, self.formInput)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editProfile.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfile))
        self.assertTrue(form.is_bound)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'bob123')
        self.assertEqual(self.user.firstName, 'bob')
        self.assertEqual(self.user.lastName, 'white')
        self.assertEqual(self.user.email, 'test@email.com')
    
    # This test checks that an update to the user profile is successful 
    # if valid data is submitted.
    # 
    #  It submits valid form data and checks that the HTTP 
    # response status code is 302, indicating a redirect. 
    # It then verifies that the response redirected to the profile page, 
    # that the correct template is used, and that a success message is displayed.
    # It also ensures that the user object is updated with the new data.
    def testSuccesfulProfileUpdate(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.formInput, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('profile')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'profile.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'johndoe2')
        self.assertEqual(self.user.firstName, 'John2')
        self.assertEqual(self.user.lastName, 'Doe2')
        self.assertEqual(self.user.email, 'johndoe2@example.org')

    

