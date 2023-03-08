''' Tests for declining a request notification'''

from ExpenseTracker.models import User, Notification
from django.test import TestCase
from django.urls import reverse

class NotificationDeclineRequestView(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.shareCategoryNotification = Notification.objects.get(id=3)

    def testNotificationIsDeletedAfterDeclining(self):
        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.delete(reverse('deleteNotifications', args=[self.shareCategoryNotification.id]))
        self.assertFalse(Notification.objects.filter(id=self.shareCategoryNotification.id).exists())
        self.assertTrue(len(userNotificationsCountBefore), len(userNotificationsCountBefore)-1)

    def testRedirectToPageBeforeAfterDeclining(self):
        urlBeforeEdit = reverse('home')
        response = self.client.post(reverse('declineRequest', args=[self.shareCategoryNotification.id]),  HTTP_REFERER=urlBeforeEdit, follow=True)
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('showUser', kwargs={'userId': self.user.id}))
        self.assertRedirects(response, reverse('logIn'))
