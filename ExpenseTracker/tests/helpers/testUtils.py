''''Tests for utility functions'''
from ExpenseTracker.models import User, Notification
from django.test import TestCase
from ExpenseTracker.helpers.notificationsHelpers import *

class Test(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defualt_objects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

    def TestNewNotificationIsCreated(self):
        userNotificationBefore = Notification.objects.filter(user=self.user).count()
        user = self.user
        title = 'Test Title'
        message = 'Test Message'
        createBasicNotification(user, title, message)
        self.assertEqual(userNotificationBefore, userNotificationBefore+1)
        newNotification = Notification.objects.get(id=3)
        self.assertEqual(newNotification.toUser, user)
        self.assertEqual(newNotification.title, title)
        self.assertEqual(newNotification.message, message)
        self.assertEqual(newNotification.isSeen, False)