from ExpenseTracker.models import User, Notification, FollowRequestNotification
from django.test import TestCase
from django.urls import reverse

class AcceptFollowRequestViewTest(TestCase):
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
        # Updating who sent the follow request notification
        self.followNotifcation = FollowRequestNotification.objects.get(id=4)
        self.followNotifcation.fromUser = self.fromUser
        self.followNotifcation.save()
        self.url = reverse('acceptFollowRequest', args=[self.followNotifcation.id])

    def testFromUserIsFollowingToUser(self):
        followersBefore = self.toUser.followerCount()
        self.client.get(self.url)
        followersAfter = self.toUser.followerCount()
        self.assertEqual(followersAfter, followersBefore+1) 
        self.assertTrue(self.toUser.followers.filter(id=self.fromUser.id).exists())
        self.assertTrue(self.fromUser.followees.filter(id=self.toUser.id).exists())


    def testFromUserRecievesNotification(self):
        self.client.get(self.url)
        latestNotification = Notification.objects.filter(toUser=self.fromUser).latest('createdAt')
        self.assertTrue(latestNotification.title, 'Follow request accepted' )
        self.assertTrue(latestNotification.message, self.toUser.username + " has accepted your follow request"  )

    def testRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('logIn'))



