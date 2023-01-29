from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, SpendingLimit
from ExpenseTracker.forms import ExpenditureForm
from django.core.paginator import Page
import datetime

class CategoryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.create(title='testexpenditure', date=datetime.date.today(), amount=10)
        spendingLimit = SpendingLimit.objects.create(amount='20', time_period='daily')
        self.category = Category.objects.create(name='testcategory', spending_limit=spendingLimit, user=self.user)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)

    def testCategoryViewGet(self):
        response = self.client.get(reverse('category', args=[self.category.name]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category.html')
        self.assertIsInstance(response.context['form'], ExpenditureForm)
        self.assertEqual(response.context['category'], self.category)
        self.assertIsInstance(response.context['expenditures'], Page)

    def testCategoryViewPost(self):
        data = {'title': 'testexpenditure2', 'date': datetime.date.today(), 'amount': 10}
        response = self.client.post(reverse('category', args=[self.category.name]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', args=[self.category.name]))
        self.assertEqual(Expenditure.objects.count(), 2)
        self.assertEqual(Expenditure.objects.first().title, 'testexpenditure2')
    
    def testCategoryViewPostWithInvalidData(self):
        data = {'title': '', 'date': '', 'amount': ''}
        response = self.client.post(reverse('category', args=[self.category.name]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', args=[self.category.name]))
        self.assertEqual(Expenditure.objects.count(), 1)
        self.assertEqual(Expenditure.objects.first().title, 'testexpenditure')

    def testCategoryViewPagination(self):
        # Create additional expenditures
        for i in range(19):
            expenditure = Expenditure.objects.create(title='testexpenditure' + str(i), date=datetime.date.today(), amount=10)
            self.category.expenditures.add(expenditure)
        # Check only 15 expenditures are displayed per page
        response = self.client.get(reverse('category', args=[self.category.name]))
        self.assertEqual(len(response.context['expenditures']), 15)
        # Check the next page displays the remaining 5 expenditures
        response = self.client.get(reverse('category', args=[self.category.name]) + '?page=2')
        self.assertEqual(len(response.context['expenditures']), 5)