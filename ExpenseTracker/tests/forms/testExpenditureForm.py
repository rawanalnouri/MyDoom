from django.test import TestCase
from django import forms
from ExpenseTracker.forms import ExpenditureForm
from ExpenseTracker.models import Expenditure, Category, SpendingLimit, User
import datetime

class ExpenditureFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        self.spendingLimit = SpendingLimit.objects.create(amount='20', timePeriod='daily')
        self.category = Category.objects.create(name='Food', spendingLimit=self.spendingLimit, user=self.user)
        self.expenditure = Expenditure.objects.create(
            title='Grocery Shopping',
            description='Weekly grocery shopping',
            amount=100.00,
            date=datetime.date.today(),
        )
        self.category.expenditures.add(self.expenditure)
    
    def testFormHasCorrectFieldsAndWidgets(self):
        form = ExpenditureForm()
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('receipt', form.fields)
        self.assertIsInstance(form.fields['amount'].widget, forms.NumberInput)
        self.assertIsInstance(form.fields['receipt'].widget, forms.FileInput)
        self.assertIsInstance(form.fields['date'].widget, forms.DateInput)

    def testFormValidation(self):
        form = ExpenditureForm({
            'title': 'Grocery Shopping',
            'description': 'Weekly grocery shopping',
            'amount': 100.00,
            'date': datetime.date.today(),
        })
        self.assertTrue(form.is_valid())

    def testFormValidationMissingFields(self):
        form = ExpenditureForm({
            'title': '',
            'description': '',
            'amount': '',
            'date': '',
        })
        self.assertFalse(form.is_valid())

    def testFormSave(self):
        form = ExpenditureForm({
            'title': 'Grocery Shopping',
            'description': 'Weekly grocery shopping',
            'amount': 100.00,
            'date': datetime.date.today(),
        })
        expenditure = form.save(self.category)
        self.assertEqual(expenditure.title, 'Grocery Shopping')
        # Verify
        self.assertTrue(expenditure in self.category.expenditures.all())
    
    def testFormUpdate(self):
        form = ExpenditureForm(instance=self.expenditure, data={
            'title': 'Updated Title',
            'description': 'Updated Description',
            'amount': 200.00,
            'date': datetime.date.today(),
        })
        self.assertTrue(form.is_valid())
        updated_expenditure = form.save(self.category)
        # Verify
        self.assertEqual(updated_expenditure.title, 'Updated Title')
        self.assertEqual(updated_expenditure.description, 'Updated Description')
        self.assertEqual(updated_expenditure.amount, 200)
        self.assertEqual(updated_expenditure.date, datetime.date.today())