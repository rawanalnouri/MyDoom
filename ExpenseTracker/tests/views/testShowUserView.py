from ExpenseTracker.models import User
from django.test import TestCase
from django.urls import reverse

class ShowUserViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

    def test_show_user_view_logged_in_user(self):
        """Test show user view with a logged in user."""
        response = self.client.get(reverse('showUser', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], self.user)
        self.assertFalse(response.context['following'])
        self.assertFalse(response.context['followable'])

    def testShowUserViewRedirectsIfUserNotLoggedIn(self):
        """Test show user view with an anonymous user."""
        self.client.logout()
        response = self.client.get(reverse('showUser', kwargs={'user_id': self.user.id}))
        self.assertRedirects(response, reverse('logIn'))

    def testShowUserViewLoggedInUser(self):
        """Test show user view with a logged in user."""
        response = self.client.get(reverse('showUser', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], self.user)
        self.assertFalse(response.context['following'])
        self.assertFalse(response.context['followable'])

    def testShowUserViewWithInvalidIdUser(self):
        """Test show user view with an invalpk user pk."""
        response = self.client.get(reverse('showUser', kwargs={'user_id': 999}))
        self.assertRedirects(response, reverse('users'))

    def testShowUserViewFollowable(self):
        """Test show user view when user is followable."""
        user2 = User.objects.create_user(
            username='testuser2',
            email='testuser2@test.com',
            password='password'
        )
        response = self.client.get(reverse('showUser', kwargs={'user_id': user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], user2)
        self.assertFalse(response.context['following'])
        self.assertTrue(response.context['followable'])

    def testShowUserViewFollowing(self):
        """Test show user view when user is being followed."""
        user2 = User.objects.create_user(
            username='testuser2',
            email='testuser2@test.com',
            password='password'
        )
        user2.followers.add(self.user)
        response = self.client.get(reverse('showUser', kwargs={'user_id': user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], user2)
        self.assertTrue(response.context['following'])
        self.assertTrue(response.context['followable'])

    def testShowUserViewSameUser(self):
        """Test show user view when user is the same user as logged in user."""
        response = self.client.get(reverse('showUser', kwargs={'user_id': self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], self.user)
        self.assertFalse(response.context['following'])
        self.assertFalse(response.context['followable'])
