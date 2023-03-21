''' Tests for form handling the user setting their overall spending limit'''

from django.test import TestCase
from django import forms
from ExpenseTracker.forms import OverallSpendingForm
from ExpenseTracker.models import User, Category, SpendingLimit, Expenditure
from decimal import Decimal

class OverallSpendingLimitFormTest(TestCase):
    # Specifies that default objects for testing purposes should be loaded into the database
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    # Initialises the user and data attributes used in the test methods
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.data = {
            'timePeriod': 'monthly',
            'amount': 1000,
        }

    # This test checks that the form is valid with valid input data
    def testValidation(self):
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertTrue(form.is_valid())

    # This test checks that the form is invalid if the amount is missing
    def testValidationWithMissingAmount(self):
        self.data['amount'] = ''
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    # This test checks that the form is invalid if the amount is negative
    def testValidationWithNegativeAmount(self):
        self.data['amount'] = -100
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    # This test checks that the form is invalid if the time period is missing
    def testValidationWithMissingTimePeriod(self):
        self.data['timePeriod'] = ''
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('timePeriod', form.errors)

    # This test checks that the form is invalid if the time period is not one of the predefined options
    def testInvalidTimePeriod(self):
        self.data['timePeriod'] = 'invalid'
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('timePeriod', form.errors)

    # This tests that the form is invalid if the total spending limit of the user's categories exceeds the overall spending limit
    def testCategoriesTotalHigherThanOverallSpendingLimit(self):
        category = Category.objects.get(id=1)
        category.users.add(self.user)
        self.user.categories.add(category)
        spendingLimit = SpendingLimit.objects.create(timePeriod='monthly', amount=1500)
        category.spendingLimit = spendingLimit
        category.save()
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertFalse(form.is_valid())
        with self.assertRaisesMessage(forms.ValidationError, 
                'Your overall spending limit is too low compared to the spending limits set'
                ' in your categories.', 
                code='invalid'
            ):
            form.clean()

    # This test checks that a yearly spending limit is converted to a monthly spending limit correctly
    def testSpendingLimitIsConvertedToMonthlyLimit(self):
        category = Category.objects.get(id=1)
        expenditure = Expenditure.objects.get(id=1)
        category.expenditures.add(expenditure)
        category.users.add(self.user)
        category.spendingLimit.timePeriod = 'yearly'
        category.save()
        self.user.categories.add(category)
        monthlyLimit = category.totalSpendingLimitByMonth()
        actualMonthlyLimit = Decimal(round((category.spendingLimit.amount/12), 2))
        self.assertEqual(monthlyLimit, actualMonthlyLimit)      