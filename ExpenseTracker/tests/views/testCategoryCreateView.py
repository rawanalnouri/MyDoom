from ExpenseTracker.models import User, Category
from django.test import TestCase
from django.urls import reverse

#tests for the create category view

class CategoryCreateViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.data = {
            'name': 'testCategory',
            'amount': 20,
            'timePeriod':'daily',
        }


    # This test checks if the view redirects to the category
    # view on successful creation of a category with valid data.
    def testCreateCategoryViewRedirectsToCategoryOnSuccess(self):
        response = self.client.post(reverse('createCategory'), self.data)
        category = Category.objects.get(name='testCategory')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category', args=[category.id]))

    # This test checks if the view displays errors when invalid data 
    # is posted to the create category form
    def testCreateCategoryViewDisplaysErrorsOnFailure(self):
        self.data['name'] = ''
        response = self.client.post(reverse('createCategory'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    # This test checks if the view redirects to the login page if 
    # the user is not logged in.
    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('createCategory'))
        self.assertRedirects(response, reverse('logIn'))
