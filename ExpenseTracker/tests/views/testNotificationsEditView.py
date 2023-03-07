''' Tests for changing if a notifications is read or unread'''

from ExpenseTracker.models import User, Notification
from django.test import TestCase
from django.urls import reverse

class DeleteNotificationViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defualt_objects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

        self.unreadNotification = Notification.objects.get(id=1)
        self.readNotification = Notification.objects.get(id=2)

    def testRedirectToPageBeforeEdit(self):
        urlBeforeEdit = reverse('home')
        response = self.client.post(reverse('editNotifications', args=[self.readNotification.id]),  HTTP_REFERER=urlBeforeEdit, follow=True)
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def testReadNotificationChangesToUnread(self):
        userReadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=True)
        userUnreadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=False)
        reverse('editNotifications', args=[self.readNotification.id])
        self.assertTrue(len(userReadNotificationsCountBefore), len(userReadNotificationsCountBefore)-1)
        self.assertTrue(len(userUnreadNotificationsCountBefore), len(userUnreadNotificationsCountBefore)+1)

    def testUneadNotificationChangesToRead(self):
        userReadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=True)
        userUnreadNotificationsCountBefore = Notification.objects.filter(toUser=self.user, isSeen=False)
        reverse('editNotifications', args=[self.unreadNotification.id])
        self.assertTrue(len(userReadNotificationsCountBefore), len(userReadNotificationsCountBefore)+1)
        self.assertTrue(len(userUnreadNotificationsCountBefore), len(userUnreadNotificationsCountBefore)-1)


