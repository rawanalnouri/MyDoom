from ExpenseTracker.models import User, Category
from django.test import TestCase
from django.urls import reverse

class CategoryCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        self.client.force_login(self.user)

    def testCreateCategoryViewRedirectsToCategoryOnSuccess(self):
        data = {
            'name': 'testcategory',
            'amount': 20,
            'timePeriod':'daily',
        }
        response = self.client.post(reverse('createCategory'), data)
        self.assertEqual(response.status_code, 302)
        category = Category.objects.get(name='testcategory')
        self.assertRedirects(response, reverse('category', args=[category.name]))

    def testCreateCategoryViewDisplaysErrorsOnFailure(self):
        data = {
            'name': '',
            'amount': 20,
            'timePeriod':'daily',
        }
        response = self.client.post(reverse('createCategory'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')