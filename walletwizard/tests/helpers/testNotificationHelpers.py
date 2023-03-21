''''Tests for creating differnt types of notifcations functions'''

from walletwizard.models import User, Notification
from django.test import TestCase
from walletwizard.helpers.notificationsHelpers import *

class NotificationHelperTest(TestCase):
    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.secondUser = User.objects.create_user(
            username='janedoe', 
            email='janedoe@example.org', 
            firstName='Jane',
            lastName='Doe',
            password='Password123',
        )
        self.title = "Test Title"
        self.message = 'Test Message'

    def testNewNotificationIsCreated(self):
        userNotificationBefore = Notification.objects.filter(toUser=self.user).count()
        user = self.user
        createBasicNotification(user, self.title, self.message)
        userNotificationAfter = Notification.objects.filter(toUser=self.user).count()
        self.assertEqual(userNotificationBefore+1, userNotificationAfter)
        newNotification = Notification.objects.filter(toUser=user).latest('createdAt')
        self.assertEqual(newNotification.toUser, user)
        self.assertEqual(newNotification.title, self.title)
        self.assertEqual(newNotification.message, self.message)
        self.assertEqual(newNotification.isSeen, False)

    def testFollowNotificationIsCreated(self):
        userNotificationBefore = Notification.objects.filter(toUser=self.user).count()
        user = self.user
        toUser = user
        fromUser = self.secondUser
        createFollowRequestNotification(toUser, self.title, self.message, fromUser)
        userNotificationAfter = Notification.objects.filter(toUser=self.user).count()
        self.assertEqual(userNotificationAfter, userNotificationBefore+1)

    def testShareNotificationIsCreated(self):
        userNotificationBefore = Notification.objects.filter(toUser=self.user).count()
        user = self.user
        category = Category.objects.get(id=1)
        toUser = user
        fromUser = self.secondUser
        createShareCategoryNotification(toUser, self.title, self.message, category, fromUser)
        userNotificationAfter = Notification.objects.filter(toUser=self.user).count()
        self.assertEqual(userNotificationAfter, userNotificationBefore+1)