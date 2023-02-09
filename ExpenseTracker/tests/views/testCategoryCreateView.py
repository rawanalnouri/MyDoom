from ExpenseTracker.models import User, Category
from django.test import TestCase
from django.urls import reverse

class CategoryCreateViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defualt_objects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

    def testCreateCategoryViewRedirectsToCategoryOnSuccess(self):
        data = {
            'name': 'testCategory',
            'amount': 20,
            'timePeriod':'daily',
        }
        response = self.client.post(reverse('createCategory'), data)
        print(response)
        self.assertEqual(response.status_code, 302)
        category = Category.objects.get(name='testCategory')
        self.assertRedirects(response, reverse('category', args=[category.id]))

    def testCreateCategoryViewDisplaysErrorsOnFailure(self):
        data = {
            'name': '',
            'amount': 20,
            'timePeriod':'daily',
        }
        response = self.client.post(reverse('createCategory'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')