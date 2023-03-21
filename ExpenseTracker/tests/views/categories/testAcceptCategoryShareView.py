# Tests for the accept category share view

from ExpenseTracker.models import User, Notification, ShareCategoryNotification
from django.test import TestCase
from django.urls import reverse

class AcceptShareCategoryViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.toUser = User.objects.get(id=1)
        self.fromUser = User.objects.create(
            username = "lucy123",
            firstName = "lucy",
            lastName = "white",
            email = "test2@email.com", 
            password = "Password123"
        )
        self.client.force_login(self.toUser)
        # Updating who sent the notification.
        self.shareNotification = ShareCategoryNotification.objects.get(id=3)
        self.shareNotification.fromUser = self.fromUser
        self.shareNotification.save()
        self.category = self.shareNotification.sharedCategory
        self.category.users.add(self.fromUser)
        self.category.save()
        self.url = reverse('acceptCategoryShare', args=[self.shareNotification.id])

    # Test ensures that when a category is shared, the number of users in the category increases by one and the toUser is added to the category.
    def testCategoryIsShared(self):
        usersBefore = self.category.users.count()
        self.client.get(self.url)
        usersAfter = self.category.users.count()
        self.assertEqual(usersAfter, usersBefore+1) 
        self.assertTrue(self.category.users.filter(id=self.toUser.id).exists())

    # Test ensures that the fromUser receives a notification after a category has been successfully shared.
    def testFromUserRecievesNotification(self):
        self.client.get(self.url)
        latestNotification = Notification.objects.filter(toUser=self.fromUser).latest('createdAt')
        self.assertTrue(latestNotification.title, 'Category share request accepted' )
        self.assertTrue(latestNotification.message, self.toUser.username + " has accepted your request to share '"+ self.category.name +"'" )

    # Test ensures that if the user is not logged in, they will be redirected to the login page before accessing the category share functionality.
    def testRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('logIn'))