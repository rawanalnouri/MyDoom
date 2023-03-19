from django.test import TestCase
from django import forms
from ExpenseTracker.forms import OverallSpendingForm
from ExpenseTracker.models import User, Category, SpendingLimit

class OverallSpendingLimitFormTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.data = {
            'timePeriod': 'monthly',
            'amount': 1000,
        }

    def testValidation(self):
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertTrue(form.is_valid())

    def testValidationWithMissingAmount(self):
        self.data['amount'] = ''
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def testValidationWithNegativeAmount(self):
        self.data['amount'] = -100
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def testValidationWithMissingTimePeriod(self):
        self.data['timePeriod'] = ''
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('timePeriod', form.errors)

    def testInvalidTimePeriod(self):
        self.data['timePeriod'] = 'invalid'
        form = OverallSpendingForm(data=self.data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('timePeriod', form.errors)

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
