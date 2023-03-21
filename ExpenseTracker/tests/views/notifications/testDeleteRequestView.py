"""Tests of delete request view."""
from ExpenseTracker.models import User, Notification
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.tests.testHelpers import reverse_with_next

class DeleteRequestViewTest(TestCase):
    """Tests of delete request view."""
    
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.shareCategoryNotification = Notification.objects.get(id=3)
        self.url = reverse('deleteRequest', args=[self.shareCategoryNotification.id])

    def testNotificationIsDeletedAfterRequestIsDeleted(self):
        urlBeforeEdit = reverse('home')
        userNotificationsCountBefore = Notification.objects.filter(toUser=self.user)
        self.client.get(self.url, HTTP_REFERER=urlBeforeEdit)
        self.assertFalse(Notification.objects.filter(id = self.shareCategoryNotification.id).exists())
        self.assertTrue(len(userNotificationsCountBefore), len(userNotificationsCountBefore) - 1)

    def testRedirectToPageBeforeAfterRequestIsDeleted(self):
        urlBeforeEdit = reverse('home')
        response = self.client.get(self.url,  HTTP_REFERER=urlBeforeEdit, follow=True)
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')