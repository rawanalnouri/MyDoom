"""Tests of category view."""
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure
import datetime
from ExpenseTracker.tests.testHelpers import reverse_with_next

class CategoryViewTest(TestCase):
    """Tests of category view."""
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.expenditure.date = datetime.datetime.now()
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
        self.url = reverse('category', args=[self.category.id])

    def testCategoryViewGet(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category.html')
        context = response.context
        self.assertEqual(context['category'], self.category)
        self.assertEqual(len(context['expenditures']), 1)
        self.assertEqual(context['expenditures'][0], self.expenditure)
    
    def testCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')

    def testCategoryViewPagination(self):
        for i in range(15):
            expenditure = Expenditure.objects.create(title='testexpenditure' + str(i), date=datetime.date.today(), amount=10)
            self.category.expenditures.add(expenditure)
        # Check only 15 expenditures are displayed per page.
        response = self.client.get(reverse('category', args=[self.category.id]))
        self.assertEqual(len(response.context['expenditures']), 10)
        # Check the next page displays the remaining 5 expenditures.
        response = self.client.get(reverse('category', args=[self.category.id]) + '?page=2')
        self.assertEqual(len(response.context['expenditures']), 6)