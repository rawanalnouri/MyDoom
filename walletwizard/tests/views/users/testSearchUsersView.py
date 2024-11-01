"""Tests of search user view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User
from walletwizard.tests.testHelpers import createUsers
from walletwizard.tests.testHelpers import reverse_with_next

class SearchUsersViewTest(TestCase):
    """Tests of search user view."""

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
        self.url = reverse('searchUsers')

    def testSearchUsersWithInvalidUsernameQuery(self):
        response = self.client.get(self.url, {'q': 'invalidusername'})
        self.assertTemplateUsed(response, 'partials/users/searchResults.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalidusername', count=0)

    def testSearchUsersWithValidUsernameQuery(self):
        # test search users with complete valid username
        response = self.client.get(self.url, {'q': 'janedoe'})
        self.assertTemplateUsed(response, 'partials/users/searchResults.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane', count=1)
        # test search users with start of valid username
        response = self.client.get(self.url, {'q': 'ja'})
        self.assertTemplateUsed(response, 'partials/users/searchResults.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane', count=1)

    def testSearchUsersWithMultipleUsersReturned(self):
        users = createUsers(15)
        response = self.client.get(self.url, {'q': 'user'})
        for user in users:
            if 'user' in user.username:
                self.assertContains(response, user.username)
        # test that the search results contain 15 users
        users = response.context['users']
        self.assertEqual(users.count(), 15)
        self.assertTemplateUsed(response, 'partials/users/searchResults.html')

    def testSearchUsersFiltersMultipleUsers(self):
        users = createUsers(15)
        response = self.client.get(self.url, {'q': 'user'})
        users = response.context['users']
        self.assertEqual(users.count(), 15)
        response = self.client.get(self.url, {'q': 'user1'})
        users = response.context['users']
        self.assertEqual(users.count(), 7)
        response = self.client.get(self.url, {'q': 'user12'})
        users = response.context['users']
        self.assertEqual(users.count(), 1)
        self.assertTemplateUsed(response, 'partials/users/searchResults.html')

    def testSearchUsersWithoutQuery(self):
        url = reverse('searchUsers')
        response = self.client.get(url)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'janedoe')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/users/searchResults.html')
    
    def testSearchUsersViewRedirectsToLoginIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('followToggle', kwargs={'userId': self.secondUser.id})
        redirectUrl = reverse_with_next('logIn', url)
        response = self.client.get(url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')