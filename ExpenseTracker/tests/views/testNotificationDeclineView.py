# Tests for the decline notification view

from ExpenseTracker.models import User, Notification
from django.test import TestCase
from django.urls import reverse

class NotificationDeclineRequestView(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.shareCategoryNotification = Notification.objects.get(id=3)

    # This test checks whether a notification is deleted after the user declines it. 
    def testNotificationIsDeletedAfterDeclining(self):
        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.get(reverse('deleteNotifications', args=[self.shareCategoryNotification.id]))
        self.assertFalse(Notification.objects.filter(id=self.shareCategoryNotification.id).exists())
        self.assertTrue(len(userNotificationsCountBefore), len(userNotificationsCountBefore)-1)

    # This test checks whether the user is redirected to the page they were on before declining the notification.
    def testRedirectToPageBeforeAfterDeclining(self):
        urlBeforeEdit = reverse('home')
        response = self.client.get(reverse('declineRequest', args=[self.shareCategoryNotification.id]),  HTTP_REFERER=urlBeforeEdit, follow=True)
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    # This test checks whether the user is redirected to the login page if they are not logged in when they try to decline a notification. 
    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('declineRequest', args=[self.shareCategoryNotification.id]))
        self.assertRedirects(response, reverse('logIn'))