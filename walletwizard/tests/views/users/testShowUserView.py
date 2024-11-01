"""Tests for show user view."""
from walletwizard.models import User
from django.test import TestCase
from django.urls import reverse
from walletwizard.tests.testHelpers import reverse_with_next

class ShowUserViewTest(TestCase):
    """Tests for show user view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.secondUser = User.objects.create_user(
            username='janedoe', 
            email='janedoe@example.org', 
            firstName='Jane',
            lastName='Doe',
            password='Password123',
        )
        self.url = reverse('showUser', kwargs={'userId': self.user.id})
        self.client.force_login(self.user)

    def testGetShowUserView(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], self.user)
        self.assertFalse(response.context['following'])
        self.assertFalse(response.context['followable'])

    def testShowUserViewRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')

    def testShowUserViewWithInvalidIdUser(self):
        response = self.client.get(reverse('showUser', kwargs={'userId': 999}))
        self.assertRedirects(response, reverse('users'))

    def testShowUserViewWhenShownUserIsFollowable(self):
        user2 = self.secondUser
        response = self.client.get(reverse('showUser', kwargs={'userId': user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], user2)
        self.assertFalse(response.context['following'])
        self.assertTrue(response.context['followable'])

    def testShowUserViewWhenUserIsFollowingShownUser(self):
        user2 = self.secondUser
        user2.followers.add(self.user)
        response = self.client.get(reverse('showUser', kwargs={'userId': user2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], user2)
        self.assertTrue(response.context['following'])
        self.assertTrue(response.context['followable'])

    def testShowUserViewWhenShownUserIsTheLoggedInUser(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'showUser.html')
        self.assertEqual(response.context['otherUser'], self.user)
        self.assertFalse(response.context['following'])
        self.assertFalse(response.context['followable'])