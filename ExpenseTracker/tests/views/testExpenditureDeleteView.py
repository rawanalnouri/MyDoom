from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, SpendingLimit
import datetime

class ExpenditureDeleteViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
        
    def testExpenditureDeleteView(self):
        response = self.client.delete(reverse('deleteExpenditure', args=[self.category.id, self.expenditure.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Expenditure.objects.filter(id=self.expenditure.id).exists())

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('showUser', kwargs={'userId': self.user.id}))
        self.assertRedirects(response, reverse('logIn'))
