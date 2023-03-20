# Tests for the expenditure delete view

from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, SpendingLimit
import datetime

class DeleteExpenditureViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
        
    #  This test case tests the functionality of deleting an expenditure. 
    def testDeleteExpenditureView(self):
        response = self.client.get(reverse('deleteExpenditure', args=[self.category.id, self.expenditure.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Expenditure.objects.filter(id=self.expenditure.id).exists())

    # This test case tests if the deleteExpenditure view redirects to the login page when the user is not logged in. 
    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('deleteExpenditure', args=[self.category.id, self.expenditure.id]))
        self.assertRedirects(response, reverse('logIn'))