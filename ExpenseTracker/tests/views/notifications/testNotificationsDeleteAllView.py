# Tests for the delete all notification view

from ExpenseTracker.models import User, Notification
from django.test import TestCase
from django.urls import reverse


class DeleteAllNotificationViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

        self.unreadNotification = Notification.objects.get(id=1)
        self.readNotification = Notification.objects.get(id=2)


    # This test creates two read notifications for the user and checks that they are deleted when the user clicks the "delete all" button. 
    def testAllReadNotificationAreDeleted(self):
        for i in range(2):
            Notification.objects.create(toUser=self.user, title='test'+str(i), message='test message', isSeen=True)

        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.get(reverse('deleteAllNotifications'))
        self.assertFalse(Notification.objects.filter(id=self.readNotification.id).exists())
        self.assertFalse(Notification.objects.filter(id=3).exists())
        self.assertFalse(Notification.objects.filter(id=4).exists())
        # Only one unread notification is not deleted
        self.assertTrue(len(userNotificationsCountBefore), 1)

    # This test checks that the user is redirected to the notifications page after clicking the "delete all" button.
    def testRedirectToNotificationsPageAfterAllDelete(self):
        response = self.client.get(reverse('deleteAllNotifications'), follow=True)
        userRedirect = reverse('notifications')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'notifications.html')

    # This test checks that an anonymous user is redirected to the login page if they try to access the "delete all" notifications page.
    def testRedirectsIfUserNotLoggedIn(self):
        """Test delete all notifications view with an anonymous user."""
        self.client.logout()
        response = self.client.get(reverse('deleteAllNotifications'))
        self.assertRedirects(response, reverse('logIn'))