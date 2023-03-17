#tests for the show user view

from ExpenseTracker.models import User
from django.test import TestCase
from django.urls import reverse

class ShowUserViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

    # This test case checks if the "show user" view is working correctly for a logged-in user. 
    def testShowUserViewLoggedInUser(self):
        """Test show user view with a logged in user."""
        response = self.client.get(reverse('showUser', kwargs={'userId': self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], self.user)
        self.assertFalse(response.context['following'])
        self.assertFalse(response.context['followable'])

    # This test case verifies that the "show user" view redirects an anonymous user to the login page if they try to access it.
    def testShowUserViewRedirectsIfUserNotLoggedIn(self):
        """Test show user view with an anonymous user."""
        self.client.logout()
        response = self.client.get(reverse('showUser', kwargs={'userId': self.user.id}))
        self.assertRedirects(response, reverse('logIn'))


    # This test case ensures that the "show user" view redirects to the "users" page if an invalid user ID is provided. 
    def testShowUserViewWithInvalidIdUser(self):
        """Test show user view with an invalpk user pk."""
        response = self.client.get(reverse('showUser', kwargs={'userId': 999}))
        self.assertRedirects(response, reverse('users'))

    # This test case checks that the "show user" view correctly sets the "followable" context variable to
    # True when the user being viewed  is not currently being followed by the logged-in user. 
    def testShowUserViewFollowable(self):
        """Test show user view when user is followable."""
        user2 = User.objects.create_user(
            username='testuser2',
            email='testuser2@test.com',
            password='password'
        )
        response = self.client.get(reverse('showUser', kwargs={'userId': user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], user2)
        self.assertFalse(response.context['following'])
        self.assertTrue(response.context['followable'])

    # This test case checks that the "show user" view correctly sets the "following" context variable 
    # to True when the user being viewed is currently being followed by the logged-in user. 
    def testShowUserViewFollowing(self):
        """Test show user view when user is being followed."""
        user2 = User.objects.create_user(
            username='testuser2',
            email='testuser2@test.com',
            password='password'
        )
        user2.followers.add(self.user)
        response = self.client.get(reverse('showUser', kwargs={'userId': user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], user2)
        self.assertTrue(response.context['following'])
        self.assertTrue(response.context['followable'])

    # This test case checks that the "show user" view correctly handles the case where the logged-in user is viewing their own profile.
    def testShowUserViewSameUser(self):
        """Test show user view when user is the same user as logged in user."""
        response = self.client.get(reverse('showUser', kwargs={'userId': self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], self.user)
        self.assertFalse(response.context['following'])
        self.assertFalse(response.context['followable'])