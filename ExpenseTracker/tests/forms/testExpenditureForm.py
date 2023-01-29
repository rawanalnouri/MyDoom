from django.test import TestCase
from django import forms
from ExpenseTracker.forms import ExpenditureForm
from ExpenseTracker.models import Expenditure, Category, SpendingLimit, User
import datetime

class ExpenditureFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        self.spendingLimit = SpendingLimit.objects.create(amount='20', time_period='daily')
        self.category = Category.objects.create(name='Food', spending_limit=self.spendingLimit, user=self.user)
        self.expenditure = Expenditure.objects.create(
            title='Grocery Shopping',
            description='Weekly grocery shopping',
            amount=100.00,
            date=datetime.date.today(),
            mood='happy'
        )
        self.category.expenditures.add(self.expenditure)
    
    def testFormHasCorrectFieldsAndWidgets(self):
        form = ExpenditureForm()
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('receipt', form.fields)
        self.assertIn('mood', form.fields)
        self.assertIsInstance(form.fields['amount'].widget, forms.NumberInput)
        self.assertIsInstance(form.fields['receipt'].widget, forms.FileInput)
        self.assertIsInstance(form.fields['mood'].widget, forms.Select)
        self.assertIsInstance(form.fields['date'].widget, forms.DateInput)

    def testFormValidation(self):
        form = ExpenditureForm({
            'title': 'Grocery Shopping',
            'description': 'Weekly grocery shopping',
            'amount': 100.00,
            'date': datetime.date.today(),
            'mood': 'happy'
        })
        self.assertTrue(form.is_valid())

    def testFormValidationMissingFields(self):
        form = ExpenditureForm({
            'title': '',
            'description': '',
            'amount': '',
            'date': '',
            'mood': ''
        })
        self.assertFalse(form.is_valid())

    def testFormSave(self):
        form = ExpenditureForm({
            'title': 'Grocery Shopping',
            'description': 'Weekly grocery shopping',
            'amount': 100.00,
            'date': datetime.date.today(),
            'mood': 'happy'
        })
        expenditure = form.save(self.category)
        self.assertEqual(expenditure.title, 'Grocery Shopping')
        self.assertTrue(expenditure in self.category.expenditures.all())