"""Tests of delete all notifications view."""
from ExpenseTracker.models import User, Notification
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.tests.testHelpers import reverse_with_next

class DeleteAllNotificationViewTest(TestCase):
    """Tests of delete all notifications view."""

    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.url = reverse('deleteAllNotifications')
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.unreadNotification = Notification.objects.get(id=1)
        self.readNotification = Notification.objects.get(id=2)

    def testAllReadNotificationAreDeleted(self):
        for i in range(2):
            Notification.objects.create(toUser=self.user, title='test'+str(i), message='test message', isSeen=True)
        userNotificationsCountBefore = Notification.objects.filter(toUser = self.user)
        self.client.get(self.url)
        self.assertFalse(Notification.objects.filter(id=self.readNotification.id).exists())
        self.assertFalse(Notification.objects.filter(id=3).exists())
        self.assertFalse(Notification.objects.filter(id=4).exists())
        # only one unread notification is not deleted
        self.assertTrue(len(userNotificationsCountBefore), 1)

    def testRedirectToNotificationsPageAfterAllDelete(self):
        response = self.client.get(self.url, follow=True)
        userRedirect = reverse('notifications')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'notifications.html')

    def testRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')