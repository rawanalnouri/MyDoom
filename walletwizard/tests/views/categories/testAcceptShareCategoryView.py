"""Tests of accept share category view."""
from walletwizard.models import User, Notification, ShareCategoryNotification
from django.test import TestCase
from django.urls import reverse
from walletwizard.tests.testHelpers import reverse_with_next

class AcceptShareCategoryViewTest(TestCase):
    """Tests of accept share category view."""
    
    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

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

        self.shareNotification = ShareCategoryNotification.objects.get(id=3)
        self.shareNotification.fromUser = self.fromUser
        self.shareNotification.save()
        self.category = self.shareNotification.sharedCategory
        self.category.users.add(self.fromUser)
        self.category.save()
        self.url = reverse('acceptCategoryShare', args=[self.shareNotification.id])

    def testCategoryIsShared(self):
        usersBefore = self.category.users.count()
        self.client.get(self.url)
        usersAfter = self.category.users.count()
        self.assertEqual(usersAfter, usersBefore+1) 
        self.assertTrue(self.category.users.filter(id=self.toUser.id).exists())

    def testFromUserRecievesNotification(self):
        self.client.get(self.url)
        latestNotification = Notification.objects.filter(toUser=self.fromUser).latest('createdAt')
        self.assertTrue(latestNotification.title, 'Category share request accepted' )
        self.assertTrue(latestNotification.message, self.toUser.username + " has accepted your request to share '"+ self.category.name +"'" )

    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')