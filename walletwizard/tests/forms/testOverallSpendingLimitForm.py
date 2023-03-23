'''Unit tests of the overall spending limit form for user.'''
from django.test import TestCase
from django import forms
from walletwizard.forms import OverallSpendingForm
from walletwizard.models import User, Category, SpendingLimit, Expenditure
from decimal import Decimal

class OverallSpendingLimitFormTest(TestCase):
    '''Unit tests of the overall spending limit form for user.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.user.categories.add(self.category)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category.expenditures.add(self.expenditure)
        self.formInput = {
            'timePeriod': 'monthly',
            'amount': 1000,
        }

    def testValidation(self):
        form = OverallSpendingForm(data=self.formInput, user=self.user)
        self.assertTrue(form.is_valid())

    def testValidationWithMissingAmount(self):
        self.formInput['amount'] = ''
        form = OverallSpendingForm(data=self.formInput, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def testValidationWithNegativeAmount(self):
        self.formInput['amount'] = -100
        form = OverallSpendingForm(data=self.formInput, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def testValidationWithMissingTimePeriod(self):
        self.formInput['timePeriod'] = ''
        form = OverallSpendingForm(data=self.formInput, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('timePeriod', form.errors)

    def testInvalidTimePeriod(self):
        self.formInput['timePeriod'] = 'invalid'
        form = OverallSpendingForm(data=self.formInput, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('timePeriod', form.errors)

    def testCategoriesTotalHigherThanOverallSpendingLimit(self):
        self.category.spendingLimit = SpendingLimit.objects.create(timePeriod='monthly', amount=1500)
        self.category.save()
        form = OverallSpendingForm(data=self.formInput, user=self.user)
        self.assertFalse(form.is_valid())
        with self.assertRaisesMessage(forms.ValidationError, 
                'Your overall spending limit is too low compared to the spending limits set'
                ' in your categories.', 
                code='invalid'
            ):
            form.clean()

    def testSpendingLimitIsConvertedToMonthlyLimit(self):
        self.category.spendingLimit.timePeriod = 'yearly'
        self.category.save()
        monthlyLimit = self.category.totalSpendingLimitByMonth()
        actualMonthlyLimit = Decimal(round((self.category.spendingLimit.amount/12), 2))
        self.assertEqual(monthlyLimit, actualMonthlyLimit)