"""Tests of users view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User
from walletwizard.tests.testHelpers import createUsers
from walletwizard.tests.testHelpers import reverse_with_next

class UserListViewTest(TestCase):
    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.url = reverse('users')
    
    def testUserListView(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('users' in response.context)
        users = response.context['users']
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'testuser')
    
    def testUserListViewPagination(self):
        createUsers(15) # 16 users total
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 10)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['users'].paginator.num_pages, 2)

    def testUserListViewPaginationSecondPage(self):
        createUsers(15) # 16 users total
        url = self.url + '?page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['users']), 6) 
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(response.context['users'].paginator.num_pages, 2)

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')