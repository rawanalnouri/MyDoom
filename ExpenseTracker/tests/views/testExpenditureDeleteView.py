from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, SpendingLimit
import datetime

#tests for the expenditure delete view

class ExpenditureDeleteViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
        
    # This test case tests the functionality of deleting an expenditure. 
    # 
    # It first sends a GET request to the deleteExpenditure view and 
    # expects a redirect response with a status code of 302. 
    # It then checks if the expenditure with the given expenditure.id 
    # exists in the database or not. If it does not exist, the test case passes. 
    # Otherwise, it fails.
    def testExpenditureDeleteView(self):
        response = self.client.get(reverse('deleteExpenditure', args=[self.category.id, self.expenditure.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Expenditure.objects.filter(id=self.expenditure.id).exists())

    #  This test case tests if the deleteExpenditure view redirects 
    # to the login page when the user is not logged in. 
    # 
    # It first logs out the user, sends a GET request to the 
    # deleteExpenditure view with the given category.id and expenditure.id, 
    # and expects a redirect response with a status code of 302. 
    # It then checks if the response redirects to the logIn view. 
    # If it does, the test case passes. 
    # Otherwise, it fails.
    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('deleteExpenditure', args=[self.category.id, self.expenditure.id]))
        self.assertRedirects(response, reverse('logIn'))