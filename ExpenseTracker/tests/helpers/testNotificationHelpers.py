''''Tests for utility functions'''
from ExpenseTracker.models import User, Notification, FollowRequestNotification
from django.test import TestCase
from ExpenseTracker.helpers.notificationsHelpers import *

class NotificationHelperTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

    def testNewNotificationIsCreated(self):
        userNotificationBefore = Notification.objects.filter(toUser=self.user).count()
        user = self.user
        title = 'Test Title'
        message = 'Test Message'
        createBasicNotification(user, title, message)
        userNotificationAfter = Notification.objects.filter(toUser=self.user).count()

        self.assertEqual(userNotificationBefore+1, userNotificationAfter)
        newNotification = Notification.objects.filter(toUser=user).latest('createdAt')
        self.assertEqual(newNotification.toUser, user)
        self.assertEqual(newNotification.title, title)
        self.assertEqual(newNotification.message, message)
        self.assertEqual(newNotification.isSeen, False)

    def testFollowNotificationIsCreated(self):
        userNotificationBefore = Notification.objects.filter(toUser=self.user).count()
        user = self.user
        secondUser = User.objects.create_user(
            username='janedoe', 
            email='janedoe@example.org', 
            firstName='Jane',
            lastName='Doe',
            password='Password123',
        )
        toUser = user
        fromUser = secondUser
        title = 'Test Title'
        message = 'Test Message'
        createFollowRequestNotification(toUser, title, message, fromUser)
        userNotificationAfter = Notification.objects.filter(toUser=self.user).count()
        self.assertEqual(userNotificationAfter, userNotificationBefore+1)
        # newNotification = Notification.objects.get(id=3)
        # self.assertEqual(newNotification.toUser, user)
        # self.assertEqual(newNotification.title, title)
        # self.assertEqual(newNotification.message, message)
        # self.assertEqual(newNotification.isSeen, False)