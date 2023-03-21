"""Tests of delete notifications view."""
from walletwizard.models import User, Notification
from django.test import TestCase
from django.urls import reverse
from walletwizard.tests.testHelpers import reverse_with_next

class DeleteNotificationViewTest(TestCase):
    """Tests of delete notifications view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
    
        self.unreadNotification = Notification.objects.get(id=1)
        self.readNotification = Notification.objects.get(id=2)
        self.url = reverse('deleteNotifications', args=[self.readNotification.id])

    def testReadNotificationIsSuccessfullyDeleted(self):
        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.get(self.url)
        self.assertFalse(Notification.objects.filter(id=self.readNotification.id).exists())
        self.assertTrue(len(userNotificationsCountBefore), len(userNotificationsCountBefore)-1)

    def testUnreadNotificationsCannotBeDeleted(self):
        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.get(reverse('deleteNotifications', args=[self.unreadNotification.id]))
        self.assertTrue(Notification.objects.filter(id=self.unreadNotification.id).exists())
        self.assertTrue(len(userNotificationsCountBefore), len(userNotificationsCountBefore))

    def testRedirectToNotificationsPageAfterDelete(self):
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