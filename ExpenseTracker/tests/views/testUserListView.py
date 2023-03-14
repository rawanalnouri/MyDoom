from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User
from ExpenseTracker.tests.helpers import createUsers

#tests for the user list view


class usersViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

    
    # This method tests the user list view. 
    # 
    # It sends a GET request to the users URL and checks if 
    # the response status code is 200 (OK). 
    # It also checks if the users variable is present in the 
    # response context and if it contains only one user with 
    # the username 'bob123'.
    def testUserListView(self):
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('users' in response.context)
        users = response.context['users']
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'bob123')
    
    # This method tests the pagination of the user list view. 
    # 
    # It creates 15 users, sends a GET request to the users URL,  
    # and checks if the response contains 10 users (the default page size), 
    # is paginated, and has two pages.
    def testUserListViewPagination(self):
        createUsers(15) # 16 users total
        url = reverse('users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 10)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['users'].paginator.num_pages, 2)

    # This method tests the pagination of the user list view for the second page. 
    # 
    # It creates 15 users, sends a GET request to the users URL with 
    # the page parameter set to 2, and checks if the response contains 6 users 
    # (the remaining users from the total of 16), is paginated,
    # and has two pages.
    def testUserListViewPaginationSecondPage(self):
        createUsers(15) # 16 users total
        url = reverse('users') + '?page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 6) 
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['users'].paginator.num_pages, 2)

    # This method tests if the user is redirected 
    # to the login page if they are not logged in. 
    # 
    # It logs out the user, sends a GET request to the users URL, 
    # and checks if the response is a redirect to the login page.
    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('users'))
        self.assertRedirects(response, reverse('logIn'))