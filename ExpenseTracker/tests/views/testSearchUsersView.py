#tests for the search user view

from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User
from ExpenseTracker.tests.helpers import createUsers

class SearchUsersViewTest(TestCase):
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
        self.url = reverse('searchUsers')


    #  This test checks whether the search function returns no results for an invalid username query. 
    def testSearchUsersWithInvalidUsernameQuery(self):
        response = self.client.get(self.url, {'q': 'invalidusername'})
        self.assertTemplateUsed(response, 'partials/users/searchResults.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'invalidusername', count=0)

    # This test checks whether the search function returns the correct result for a valid username query.
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

    # This test checks whether the search function returns the correct number of results when there are multiple users in the system. 
    def testSearchUsersWithMultipleUsersReturned(self):
        users = createUsers(15)
        response = self.client.get(self.url, {'q': 'user'})
        for user in users:
            if 'user' in user.username:
                self.assertContains(response, user.username)
            else:
                self.assertContains(response, user.username, count=0)
        # test that the search results contain 15 users
        users = response.context['users']
        self.assertEqual(users.count(), 15)
        self.assertTemplateUsed(response, 'partials/users/searchResults.html')

    # This test checks whether the search function filters the search results correctly based on the search query. 
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

    # This test checks whether the search function returns all users in the system when no search query is provided. 
    def testSearchUsersWithoutQuery(self):
        url = reverse('searchUsers')
        response = self.client.get(url)
        self.assertContains(response, 'bob123')
        self.assertContains(response, 'janedoe')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/users/searchResults.html')