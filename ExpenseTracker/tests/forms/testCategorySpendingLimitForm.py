from django.test import TestCase
from django import forms
from ExpenseTracker.models import Category, SpendingLimit, User
from ExpenseTracker.forms import CategorySpendingLimitForm

class CategorySpendingLimitFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        self.spendingLimit = SpendingLimit.objects.create(amount='20', time_period='daily')
        self.category = Category.objects.create(name='Test Category', spending_limit=self.spendingLimit, user=self.user)
        self.data = {
            'name': 'Test Category',
            'description': 'This is a test category',
            'time_period': 'weekly',
            'amount': 10
        }
    
    def testFormHasCorrectFieldsAndWidgets(self):
        form = CategorySpendingLimitForm(user=self.user)
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('time_period', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIsInstance(form.fields['time_period'].widget, forms.Select)
        self.assertIsInstance(form.fields['amount'].widget, forms.NumberInput)

    def testFormValidation(self):
        form = CategorySpendingLimitForm(data=self.data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def testFormValidationMissingFields(self):
        form = CategorySpendingLimitForm({
            'name': '',
            'description': '',
            'time_period': '',
            'amount': ''
        }, user=self.user)
        self.assertFalse(form.is_valid())

    def testFormSave(self):
        form = CategorySpendingLimitForm(data=self.data, user=self.user)
        form.is_valid()
        category = form.save()
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(category.description, 'This is a test category')
        self.assertEqual(category.user, self.user)
        self.assertEqual(category.spending_limit.time_period, 'weekly')
        self.assertEqual(category.spending_limit.amount, 10)

    def testFormUpdate(self):
        form = CategorySpendingLimitForm(data=self.data, instance=self.category, user=self.user)
        form.is_valid()
        category = form.save()
        self.assertEqual(category.name, 'Test Category')
        self.assertEqual(category.description, 'This is a test category')
        self.assertEqual(category.user, self.user)
        self.assertEqual(category.spending_limit.time_period, 'weekly')
        self.assertEqual(category.spending_limit.amount, 10)