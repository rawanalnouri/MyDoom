"""Tests of edit notification view."""
from walletwizard.models import User, Notification
from django.test import TestCase
from django.urls import reverse
from walletwizard.tests.testHelpers import reverse_with_next

class EditNotificationViewTest(TestCase):
    """Tests of edit notification view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.unreadNotification = Notification.objects.get(id=1)
        self.readNotification = Notification.objects.get(id=2)
        self.url = reverse('editNotifications', args=[self.readNotification.id])

    def testRedirectToPageBeforeEdit(self):
        urlBeforeEdit = reverse('home')
        response = self.client.get(self.url,  HTTP_REFERER=urlBeforeEdit, follow=True)
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def testReadNotificationChangesToUnread(self):
        userReadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=True)
        userUnreadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=False)
        reverse('editNotifications', args=[self.readNotification.id])
        self.assertTrue(len(userReadNotificationsCountBefore), len(userReadNotificationsCountBefore)-1)
        self.assertTrue(len(userUnreadNotificationsCountBefore), len(userUnreadNotificationsCountBefore)+1)

    def testUneadNotificationChangesToRead(self):
        userReadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=True)
        userUnreadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=False)
        reverse('editNotifications', args=[self.unreadNotification.id])
        self.assertTrue(len(userReadNotificationsCountBefore), len(userReadNotificationsCountBefore)+1)
        self.assertTrue(len(userUnreadNotificationsCountBefore), len(userUnreadNotificationsCountBefore)-1)
    
    def testRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')