# Tests for the user list view

from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User
from ExpenseTracker.tests.helpers import createUsers

class usersViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
    
    #  This method tests the user list view. 
    def testUserListView(self):
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('users' in response.context)
        users = response.context['users']
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'bob123')
    
    #  This method tests the pagination of the user list view. 
    def testUserListViewPagination(self):
        createUsers(15) # 16 users total
        url = reverse('users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 10)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['users'].paginator.num_pages, 2)

    #  This method tests the pagination of the user list view for the second page. 
    def testUserListViewPaginationSecondPage(self):
        createUsers(15) # 16 users total
        url = reverse('users') + '?page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 6) 
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['users'].paginator.num_pages, 2)

    #  This method tests if the user is redirected to the login page if they are not logged in. 
    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('users'))
        self.assertRedirects(response, reverse('logIn'))