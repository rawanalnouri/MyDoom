from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.forms import ReportForm
from ExpenseTracker.models import *
import datetime
from ExpenseTracker.helpers.reportsHelpers import *
from dateutil.relativedelta import relativedelta



class ReportsHelpersTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.expenditure.date = datetime.now()
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.user.save()
        self.category.users.add(self.user)
        self.category.expenditures.add(self.expenditure)
        self.category.save()
        self.input = {
            "timePeriod": "month",
            "selectedCategory": self.category.id
        }
        self.form = ReportForm(user=self.user, data=input)

    def testWeeklyBudgetIsCovertedToDaily(self):
        self.category.spendingLimit.timePeriod = 'weekly'
        changedBudget = convertBudgetToDaily(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount/7)

    def testMonthyBudgetIsCovertedToDaily(self):
        self.category.spendingLimit.timePeriod = 'monthly'
        changedBudget = convertBudgetToDaily(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount/30)

    def testYearlyBudgetIsCovertedToDaily(self):
        self.category.spendingLimit.timePeriod = 'yearly'
        changedBudget = convertBudgetToDaily(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount/365)

    def testDailyyBudgetIsCovertedToDaily(self):
        self.category.spendingLimit.timePeriod = 'daily'
        changedBudget = convertBudgetToDaily(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount)


    def testWeeklyBudgetIsCovertedToWeekly(self):
        self.category.spendingLimit.timePeriod = 'daily'
        changedBudget = convertBudgetToWeekly(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount*7)

    def testMonthyBudgetIsCovertedToWeekly(self):
        self.category.spendingLimit.timePeriod = 'monthly'
        changedBudget = convertBudgetToWeekly(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount/4)

    def testYearlyBudgetIsCovertedToWeekly(self):
        self.category.spendingLimit.timePeriod = 'yearly'
        changedBudget = convertBudgetToWeekly(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount/52)

    def testDailyyBudgetIsCovertedToWeekly(self):
        self.category.spendingLimit.timePeriod = 'weekly'
        changedBudget = convertBudgetToWeekly(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount)

    def testWeeklyBudgetIsCovertedToMonthly(self):
        self.category.spendingLimit.timePeriod = 'daily'
        changedBudget = convertBudgetToMonthly(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount*30)

    def testMonthyBudgetIsCovertedToMonthly(self):
        self.category.spendingLimit.timePeriod = 'monthly'
        changedBudget = convertBudgetToMonthly(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount)

    def testYearlyBudgetIsCovertedToMonthly(self):
        self.category.spendingLimit.timePeriod = 'yearly'
        changedBudget = convertBudgetToMonthly(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount/12)

    def testDailyyBudgetIsCovertedToMonthly(self):
        self.category.spendingLimit.timePeriod = 'weekly'
        changedBudget = convertBudgetToMonthly(self.category)
        self.assertEqual(changedBudget, self.category.spendingLimit.amount*4)

    def testCreateArraysDataForDailyLimit(self):
        self.category.spendingLimit.timePeriod = 'day'
        self.category.save()
        # Generate a graph for historical data with filter
        first_day_this_month = datetime.now().replace(day=1)
        first_day_next_month = (first_day_this_month + timedelta(days=32)).replace(day=1)
        first_day_twelve_months_ago = first_day_next_month - relativedelta(years=1)
        yearData = createArraysData([self.category.id], self.category.spendingLimit.timePeriod, first_day_twelve_months_ago, [365, 52, 12])
        categorySpend = float(self.expenditure.amount/365)
        expectedYearData = round((categorySpend/float(convertBudgetToDaily(self.category))*100),2)
        self.assertEqual(yearData[0], expectedYearData)

        # Generate a graph for historical data without filter (non-historical data)
        yearData = createArraysData([self.category.id], self.category.spendingLimit.timePeriod)
        categorySpend = float(self.expenditure.amount/365)
        expectedYearData = round((categorySpend/float(convertBudgetToDaily(self.category))*100),2)
        self.assertEqual(yearData[0][0], self.category.name)
        self.assertEqual(yearData[1][0], 0)


    def testCreateArraysDataForWeeklyLimit(self):
        self.category.spendingLimit.timePeriod = 'week'
        self.category.save()
        # Generate a graph for historical data with filter
        first_day_this_month = datetime.now().replace(day=1)
        first_day_next_month = (first_day_this_month + timedelta(days=32)).replace(day=1)
        first_day_twelve_months_ago = first_day_next_month - relativedelta(years=1)
        yearData = createArraysData([self.category.id], self.category.spendingLimit.timePeriod, first_day_twelve_months_ago, [365, 52, 12])
        categorySpend = float(self.expenditure.amount/365)
        expectedYearData = round((categorySpend/float(convertBudgetToDaily(self.category))*100),2)
        self.assertEqual(yearData[0], expectedYearData)

        # Generate a graph for historical data without filter (non-historical data)
        yearData = createArraysData([self.category.id], self.category.spendingLimit.timePeriod)
        categorySpend = float(self.expenditure.amount/365)
        expectedYearData = round((categorySpend/float(convertBudgetToDaily(self.category))*100),2)
        self.assertEqual(yearData[0][0], self.category.name)
        self.assertEqual(yearData[1][0], 0)
