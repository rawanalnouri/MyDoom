from ExpenseTracker.models import User, Notification, FollowRequestNotification
from django.test import TestCase
from django.urls import reverse

#tests for the accept follow request view

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

    # This test ensures that when a user sends a follow request to another user, 
    # the toUser's follower count increases by 1 and the fromUser is added to 
    # the toUser's followers list and the toUser is added to the 
    # fromUser's followees list.
    def testFromUserIsFollowingToUser(self):
        followersBefore = self.toUser.followerCount()
        self.client.get(self.url)
        followersAfter = self.toUser.followerCount()
        self.assertEqual(followersAfter, followersBefore+1) 
        self.assertTrue(self.toUser.followers.filter(id=self.fromUser.id).exists())
        self.assertTrue(self.fromUser.followees.filter(id=self.toUser.id).exists())


    # This test ensures that when a user accepts a follow request, 
    # a notification is created for the fromUser with the message 
    # "user has accepted your follow request".
    def testFromUserRecievesNotification(self):
        self.client.get(self.url)
        latestNotification = Notification.objects.filter(toUser=self.fromUser).latest('createdAt')
        self.assertTrue(latestNotification.title, 'Follow request accepted' )
        self.assertTrue(latestNotification.message, self.toUser.username + " has accepted your follow request"  )

    # This test ensures that a user is redirected to the 
    # login page if they are not logged in when trying to 
    # follow another user.
    def testRedirectsIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('logIn'))



