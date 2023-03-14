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


    def testCreateCategoryViewRedirectsToCategoryOnSuccess(self):
        response = self.client.post(reverse('createCategory'), self.data)
        category = Category.objects.get(name='testCategory')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category', args=[category.id]))

    def testCreateCategoryViewDisplaysErrorsOnFailure(self):
        self.data['name'] = ''
        response = self.client.post(reverse('createCategory'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('createCategory'))
        self.assertRedirects(response, reverse('logIn'))
