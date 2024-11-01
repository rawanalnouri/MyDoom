"""Tests for the home view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User, Category, Expenditure, SpendingLimit
from walletwizard.tests.testHelpers import reverse_with_next
import datetime

class HomeViewTest(TestCase):
    """Tests for the home view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

        self.expenditure = Expenditure.objects.get(id=1)
        self.expenditure.date = datetime.datetime.now()
        self.expenditure.save()
        self.category = Category.objects.get(id=1)
        self.category.expenditures.add(self.expenditure)
        self.category.users.add(self.user)
        self.category.save()
        self.user.categories.add(self.category)
        self.user.save()
        self.spendingLimit = SpendingLimit.objects.get(id=1)

    def testHomeViewUsesCorrectTemplate(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def testHomeViewRedirectsToLoginIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')

    def testCorrectMonthlyTotalSpentForEachCategory(self):
        totalSpentThisMonth = self.expenditure.amount
        categorySpentThisMonth = self.expenditure.amount
        response = self.client.get(self.url)
        self.assertEqual(totalSpentThisMonth, self.user.totalSpentThisMonth())
        self.assertEqual(categorySpentThisMonth, response.context['data'][0])

    def testCorrectDailyLimitTotalSpentDataIsGenerated(self):
        self.category.spendingLimit.timePeriod = 'daily'
        self.category.save()
        totalSpentThisDay = self.expenditure.amount
        categorySpentThisDay = self.expenditure.amount
        response = self.client.get(self.url)
        self.assertEqual(totalSpentThisDay, self.category.totalSpentInTimePeriod())
        self.assertEqual(categorySpentThisDay, response.context['data'][0])

    def testCorrectWeeklyLimitTotalSpentDataIsGenerated(self):
        self.category.spendingLimit.timePeriod = 'weekly'
        self.category.save()
        totalSpentThisDay = self.expenditure.amount
        categorySpentThisWeek = self.expenditure.amount
        response = self.client.get(self.url)
        self.assertEqual(totalSpentThisDay, self.category.totalSpentInTimePeriod())
        self.assertEqual(categorySpentThisWeek, response.context['data'][0])

    def testCorrectMonthlyLimitTotalSpentDataIsGenerated(self):
        self.category.spendingLimit.timePeriod = 'monthly'
        self.category.save()
        totalSpentThisMonth = self.expenditure.amount
        categorySpentThisMonth = self.expenditure.amount
        response = self.client.get(self.url)
        self.assertEqual(totalSpentThisMonth, self.category.totalSpentInTimePeriod())
        self.assertEqual(categorySpentThisMonth, response.context['data'][0])

    def testCorrectYearlyLimitTotalSpentDataIsGenerated(self):
        self.category.spendingLimit.timePeriod = 'yearly'
        self.category.save()
        totalSpentThisYear = self.expenditure.amount
        categorySpentThisYear = self.expenditure.amount
        response = self.client.get(self.url)
        self.assertEqual(totalSpentThisYear, self.category.totalSpentInTimePeriod())
        self.assertEqual(categorySpentThisYear, response.context['data'][0])        