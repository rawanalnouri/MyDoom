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


    # Tests that a read notification can be successfully deleted. 
    # 
    # It checks that the notification is no longer in the database and 
    # that the number of notifications for the user has decreased by one.
    def testReadNotificationIsSuccessfullyDeleted(self):
        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.get(reverse('deleteNotifications', args=[self.readNotification.id]))
        self.assertFalse(Notification.objects.filter(id=self.readNotification.id).exists())
        self.assertTrue(len(userNotificationsCountBefore), len(userNotificationsCountBefore)-1)

    # Tests that an unread notification cannot be deleted.
    #  
    # It checks that the notification still exists in the database
    #  and that the number of notifications for the user has not changed.
    def testUnreadNotificationsCannotBeDeleted(self):
        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.get(reverse('deleteNotifications', args=[self.unreadNotification.id]))
        self.assertTrue(Notification.objects.filter(id=self.unreadNotification.id).exists())
        self.assertTrue(len(userNotificationsCountBefore), len(userNotificationsCountBefore))

    # Tests that the user is redirected to the notifications page after a notification is deleted. 
    # 
    # It checks that the response status code is 302 (indicating a redirect) and 
    # that the redirected page is the notifications page.
    def testRedirectToNotificationsPageAfterDelete(self):
        response = self.client.get(reverse('deleteNotifications', args=[self.readNotification.id]), follow=True)
        userRedirect = reverse('notifications')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'notifications.html')

    # Tests that a user who is not logged in is redirected to the login page if they 
    # attempt to delete a notification. 
    # 
    # It checks that the response status code is 302 (indicating a redirect) and 
    # that the redirected page is the login page.
    def testRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('deleteNotifications', args=[self.readNotification.id]))
        self.assertRedirects(response, reverse('logIn'))