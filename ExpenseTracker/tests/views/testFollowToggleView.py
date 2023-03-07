from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from ExpenseTracker.models import User, Category, Notification
from ExpenseTracker.helpers.utils import toggleFollow

class FollowToggleViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

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
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.users.add(self.user)

    def _acceptFollowRequest(self):
        notification = Notification.objects.filter(toUser=self.secondUser).latest('createdAt')
        acceptUrl = reverse('acceptFollowRequest', args=[notification.id])
        return self.client.get(acceptUrl)


    def testFollowToggleViewFollowUser(self):
        followResponse = self.client.get(reverse('followToggle', kwargs={'userId': self.secondUser.id}))
        self.assertEqual(followResponse.status_code, 302)
        acceptResponse = self._acceptFollowRequest()
        self.assertEqual(acceptResponse.status_code, 302)
        self.assertIn(self.user, self.secondUser.followers.all())
    
    def testFollowToggleViewUnfollowUser(self):
        toggleFollow(self.user, self.secondUser)
        acceptResponse = self._acceptFollowRequest()
        self.assertEqual(acceptResponse.status_code, 302)
        self.assertIn(self.user, self.secondUser.followers.all())
        response = self.client.get(reverse('followToggle', kwargs={'userId': self.secondUser.id}))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user, self.secondUser.followers.all())

    def testFollowToggleViewInvalidUser(self):
        response = self.client.get(reverse('followToggle', kwargs={'userId': 999}))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(id=999)
    
    def testFollowToggleViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('followToggle', kwargs={'userId': self.secondUser.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
