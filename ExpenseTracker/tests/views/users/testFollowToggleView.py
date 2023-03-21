"""Tests of follow toggle view."""
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from ExpenseTracker.models import User, Category, FollowRequestNotification
from ExpenseTracker.helpers.followHelpers import toggleFollow
from ExpenseTracker.tests.testHelpers import reverse_with_next

class FollowToggleViewTest(TestCase):
    """Tests of follow toggle view."""

    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.secondUser = User.objects.create_user(
            username='janedoe', 
            email='janedoe@example.org', 
            firstName='Jane',
            lastName='Doe',
            password='Password123',
        )
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.users.add(self.user)
        self.url = reverse('followToggle', kwargs={'userId': self.secondUser.id})

    def _acceptFollowRequest(self, user):
        notification = FollowRequestNotification.objects.filter(toUser=user).latest('createdAt')
        acceptUrl = reverse('acceptFollowRequest', args=[notification.id])
        return self.client.get(acceptUrl)

    def testFollowToggleViewFollowUser(self):
        followResponse = self.client.get(self.url)
        self.assertEqual(followResponse.status_code, 302)
        acceptResponse = self._acceptFollowRequest(self.secondUser)
        self.assertEqual(acceptResponse.status_code, 302)
        self.assertIn(self.user, self.secondUser.followers.all())

    def testUserCannotFollowThemselves(self):
        followersBefore = self.user.followeeCount()
        self.client.get(reverse('followToggle', kwargs={'userId': self.user.id}))
        followersAfter = self.user.followeeCount()
        self.assertEqual(followersAfter, followersBefore)
    
    def testFollowToggleViewUnfollowUser(self):
        toggleFollow(self.user, self.secondUser)
        acceptResponse = self._acceptFollowRequest(self.secondUser)
        self.assertEqual(acceptResponse.status_code, 302)
        self.assertIn(self.user, self.secondUser.followers.all())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user, self.secondUser.followers.all())

    def testFollowToggleViewInvalidUser(self):
        response = self.client.get(reverse('followToggle', kwargs={'userId': 999}))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(id=999)

    def testUserRecievesFollowRequestNotification(self):
        self.client.get(self.url)
        notificationReceived = FollowRequestNotification.objects.filter(toUser=self.secondUser).latest('createdAt')
        self.assertEqual(notificationReceived.title, "New follow request!")
        self.assertEqual(notificationReceived.message, self.user.username + " wants to follow you")
        self.assertEqual(notificationReceived.fromUser, self.user)

    def testFollowToggleViewRedirectsIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')