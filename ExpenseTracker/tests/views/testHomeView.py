from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure
import datetime


class HomeViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defualt_objects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.expenditure.date = datetime.datetime.now()
        self.expenditure.save()
        self.category = Category.objects.get(id=1)
        self.category.expenditures.add(self.expenditure)
        self.category.save()
        self.category.users.add(self.user)
        self.category.save()
        self.user.categories.add(self.category)
        self.user.save()


    def testHomeViewUsesCorrectTemplate(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def testHomeViewRedirectsToLoginIfNotLoggedIn(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/logIn/')

    def testCorrectMonthlyTotalSpentForEachCategory(self):
        totalSpentThisMonth = self.expenditure.amount
        categorySpentThisMonth = self.expenditure.amount
        response = self.client.get(reverse('home'))
        self.assertEqual(totalSpentThisMonth, self.user.totalSpentThisMonth())
        self.assertEqual(categorySpentThisMonth, response.context['data'][0])



