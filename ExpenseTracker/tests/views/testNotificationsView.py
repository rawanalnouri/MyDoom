''''Tests for page showing all read and unread notifications'''
from ExpenseTracker.models import User, Notification
from django.test import TestCase
from django.urls import reverse
from django.core.paginator import Page

#tests for the notification view


class DeleteAllNotificationViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

        self.unreadNotification = Notification.objects.get(id=1)
        self.readNotification = Notification.objects.get(id=2)

    # This test ensures that the notifications view is accessible 
    # and that the correct template is being used.
    #  
    # It also checks that the pagination objects returned in the context
    # are instances of Page. Additionally, it confirms that the context 
    # processor context is available and that the number of unread and 
    # read notifications in the context match the corresponding objects in 
    # the database for the logged-in user.
    def testNotificationViewGet(self):
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications.html')
        self.assertIsInstance(response.context['unreadNotificationsPaginated'], Page)
        self.assertIsInstance(response.context['readNotificationsPaginated'], Page)
        #Check contextProcessor context is available
        self.assertEqual(len(response.context['unreadNotifications']), len(Notification.objects.filter(toUser=self.user, isSeen=False)))
        self.assertEqual(len(response.context['readNotifications']), len(Notification.objects.filter(toUser=self.user, isSeen=True)))

    # This test creates additional unread notifications and checks that only 
    # 5 notifications are displayed per page. 
    # 
    # It then checks that the next page displays the remaining unread notifications.
    def testUnreadNotificationsPagination(self):
        # Create additional unread notifications
        for i in range(5):
            Notification.objects.create(toUser=self.user, title='test'+str(i), message='test message', isSeen=False, type="basic")
        # Check only 5 expenditures are displayed per page
        response = self.client.get(reverse('notifications'))
        self.assertEqual(len(response.context['unreadNotificationsPaginated']), 5)
        # Check the next page displays the remaining 1 notifications
        response = self.client.get(reverse('notifications') + '?page=2')
        self.assertEqual(len(response.context['unreadNotificationsPaginated']), 1)

    # This test creates additional read notifications and checks that only 5 
    # notifications are displayed per page. 
    # 
    # It then checks that the next page displays the remaining read notifications.
    def testReadNotificationsPagination(self):
        # Create additional unread notifications
        for i in range(9):
            Notification.objects.create(toUser=self.user, title='test'+str(i), message='test message', isSeen=True, type="basic")
        # Check only 5 expenditures are displayed per page
        response = self.client.get(reverse('notifications'))
        self.assertEqual(len(response.context['readNotificationsPaginated']), 5)
        # Check the next page displays the remaining 5 notifications
        response = self.client.get(reverse('notifications') + '?page=2')
        self.assertEqual(len(response.context['readNotificationsPaginated']), 5)

    # This test logs out the user and ensures that attempting to access the 
    # notifications view redirects to the login page.
    def testRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('notifications'))
        self.assertRedirects(response, reverse('logIn'))