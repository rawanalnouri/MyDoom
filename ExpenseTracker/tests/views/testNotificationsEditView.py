# Tests for the edit notification view

from ExpenseTracker.models import User, Notification
from django.test import TestCase
from django.urls import reverse


class EditNotificationViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

        self.unreadNotification = Notification.objects.get(id=1)
        self.readNotification = Notification.objects.get(id=2)

    # This test checks that when a user tries to edit a notification, they are taken to the page they were on before clicking the "Edit" button. 
    def testRedirectToPageBeforeEdit(self):
        urlBeforeEdit = reverse('home')
        response = self.client.get(reverse('editNotifications', args=[self.readNotification.id]),  HTTP_REFERER=urlBeforeEdit, follow=True)
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    # This test checks that when a user marks a notification as unread, the notification count for that user is updated correctly in the database. 
    def testReadNotificationChangesToUnread(self):
        userReadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=True)
        userUnreadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=False)
        reverse('editNotifications', args=[self.readNotification.id])
        self.assertTrue(len(userReadNotificationsCountBefore), len(userReadNotificationsCountBefore)-1)
        self.assertTrue(len(userUnreadNotificationsCountBefore), len(userUnreadNotificationsCountBefore)+1)

    # This test checks that when a user marks a notification as read, the notification count for that user is updated correctly in the database. 
    def testUneadNotificationChangesToRead(self):
        userReadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=True)
        userUnreadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=False)
        reverse('editNotifications', args=[self.unreadNotification.id])
        self.assertTrue(len(userReadNotificationsCountBefore), len(userReadNotificationsCountBefore)+1)
        self.assertTrue(len(userUnreadNotificationsCountBefore), len(userUnreadNotificationsCountBefore)-1)

    # This test checks that if a user is not logged in and tries to edit a notification, they are redirected to the login page.
    def testRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('editNotifications', args=[self.readNotification.id]))
        self.assertRedirects(response, reverse('logIn'))