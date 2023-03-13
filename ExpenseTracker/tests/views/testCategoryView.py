from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure
import datetime

class CategoryViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.expenditure.date = datetime.datetime.now()
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)

    def test_category_view_get(self):
        url = reverse('category', args=[self.category.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category.html')

        context = response.context
        self.assertEqual(context['category'], self.category)
        self.assertEqual(len(context['expenditures']), 1)
        self.assertEqual(context['expenditures'][0], self.expenditure)
    
    def testCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('category', kwargs={'categoryId': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')
