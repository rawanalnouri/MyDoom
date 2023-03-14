''' Tests for deleting a single read notification'''

from ExpenseTracker.models import User, Notification
from django.test import TestCase
from django.urls import reverse

#tests for the delete notification view

class DeleteNotificationViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

        self.unreadNotification = Notification.objects.get(id=1)
        self.readNotification = Notification.objects.get(id=2)

    def testReadNotificationIsSuccessfullyDeleted(self):
        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.get(reverse('deleteNotifications', args=[self.readNotification.id]))
        self.assertFalse(Notification.objects.filter(id=self.readNotification.id).exists())
        self.assertTrue(len(userNotificationsCountBefore), len(userNotificationsCountBefore)-1)

    def testUnreadNotificationsCannotBeDeleted(self):
        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.get(reverse('deleteNotifications', args=[self.unreadNotification.id]))
        self.assertTrue(Notification.objects.filter(id=self.unreadNotification.id).exists())
        self.assertTrue(len(userNotificationsCountBefore), len(userNotificationsCountBefore))

    def testRedirectToNotificationsPageAfterDelete(self):
        response = self.client.get(reverse('deleteNotifications', args=[self.readNotification.id]), follow=True)
        userRedirect = reverse('notifications')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'notifications.html')

    def testRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('deleteNotifications', args=[self.readNotification.id]))
        self.assertRedirects(response, reverse('logIn'))