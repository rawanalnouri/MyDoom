from django.test import TestCase
from django import forms
from ExpenseTracker.models import Category, SpendingLimit, User
from ExpenseTracker.forms import CategorySpendingLimitForm

class CategorySpendingLimitFormTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.data = {
            'name': 'Food',
            'description': 'This is a test category',
            'timePeriod': 'weekly',
            'amount': 10
        }
    
    def testFormHasCorrectFieldsAndWidgets(self):   
        form = CategorySpendingLimitForm(user=self.user)
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('timePeriod', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIsInstance(form.fields['timePeriod'].widget, forms.Select)
        self.assertIsInstance(form.fields['amount'].widget, forms.NumberInput)

    def testFormValidation(self):
        form = CategorySpendingLimitForm(data=self.data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def testFormValidationMissingFields(self):
        form = CategorySpendingLimitForm({
            'name': '',
            'description': '',
            'timePeriod': '',
            'amount': ''
        }, user=self.user)
        self.assertFalse(form.is_valid())

    def testFormSave(self):
        form = CategorySpendingLimitForm(data=self.data, user=self.user)
        form.is_valid()
        category = form.save()
        self.assertEqual(category.name, 'Food')
        self.assertEqual(category.description, 'This is a test category')
        self.assertTrue(self.user in self.category.users.all())
        self.assertEqual(category.spendingLimit.timePeriod, 'weekly')
        self.assertEqual(category.spendingLimit.amount, 10)

    def testFormUpdate(self):
        form = CategorySpendingLimitForm(data=self.data, instance=self.category, user=self.user)
        form.is_valid()
        category = form.save()
        self.assertEqual(category.name, 'Food')
        self.assertEqual(category.description, 'This is a test category')
        self.assertTrue(self.user in self.category.users.all())
        self.assertEqual(category.spendingLimit.timePeriod, 'weekly')
        self.assertEqual(category.spendingLimit.amount, 10)