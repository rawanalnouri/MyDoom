# Tests for the create category view

from ExpenseTracker.models import User, Category, SpendingLimit
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

class CategoryCreateViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.data = {
            'name': 'Food',
            'amount': 20,
            'timePeriod':'daily',
        }

    # This test checks if the view redirects to the category view on successful creation of a category with valid data.
    def testCreateCategoryViewRedirectsToCategoryOnSuccess(self):
        response = self.client.post(reverse('createCategory'), self.data)
        category = Category.objects.get(name='Food')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category', args=[category.id]))

    # This test checks if the view displays errors when invalid data is posted to the create category form
    def testCreateCategoryViewDisplaysErrorsOnFailure(self):
        self.data['name'] = ''
        response = self.client.post(reverse('createCategory'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    # This test checks if the view redirects to the login page if the user is not logged in.
    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('createCategory'))
        self.assertRedirects(response, reverse('logIn'))

    #  Tests if the correct error is displayed when a category is created
    def testCreateCategoryViewSameNameError(self):
        spendingLimit = SpendingLimit.objects.create(timePeriod='weekly', amount=10)
        category = Category.objects.create(name='SameName', description='This is another test category', spendingLimit=spendingLimit)
        category.users.add(self.user)
         # Create a post request data with the same name as the existing category.
        postData = {
            'name': 'SameName',
            'description': 'This is a new test category',
            'timePeriod': 'daily',
            'amount': 5
        }
        response = self.client.post(reverse('createCategory'), data=postData)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Category with this name already exists for this user.")
        self.assertEqual(messages[0].level_tag, "danger")