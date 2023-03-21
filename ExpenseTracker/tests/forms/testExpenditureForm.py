''' Tests for form handling the creation of expenditures'''

from django.test import TestCase
from django import forms
from ExpenseTracker.forms import ExpenditureForm
from ExpenseTracker.models import Expenditure, Category, SpendingLimit, User
import datetime

class ExpenditureFormTest(TestCase):
    # Create instances of User, SpendingLimit, Category, and Expenditure models that are required for the tests
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        self.spendingLimit = SpendingLimit.objects.create(amount='20', timePeriod='daily')
        self.category = Category.objects.create(name='Food', spendingLimit=self.spendingLimit)
        self.category.users.add(self.user)
        self.expenditure = Expenditure.objects.create(
            title='Grocery Shopping',
            description='Weekly grocery shopping',
            amount=100.00,
            date=datetime.date.today(),
        )
        self.category.expenditures.add(self.expenditure)
    
    # This tests whether the form has the correct fields and widgets
    def testFormHasCorrectFieldsAndWidgets(self):
        form = ExpenditureForm(self.user, self.category)
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('receipt', form.fields)
        self.assertIsInstance(form.fields['amount'].widget, forms.NumberInput)
        self.assertIsInstance(form.fields['receipt'].widget, forms.FileInput)
        self.assertIsInstance(form.fields['date'].widget, forms.DateInput)

    # This test checks whether the form validates correctly with valid data
    def testFormValidation(self):
        data = {
            'title': 'Grocery Shopping',
            'description': 'Weekly grocery shopping',
            'amount': 100.00,
            'date': datetime.date.today(),
            'otherCategory': -1,
        }
        form = ExpenditureForm(self.user, self.category, data)
        self.assertTrue(form.is_valid())

    # This tests whether the form fails validation when required fields are missing
    def testFormValidationMissingFields(self):
        data = {
            'title': '',
            'description': '',
            'amount': '',
            'date': '',
            'otherCategory': '',
        }
        form = ExpenditureForm(self.user, self.category, data)
        self.assertFalse(form.is_valid())

    # This test checks if the form can save the data correctly and the instance is added to the corresponding category
    def testFormSave(self):
        form = ExpenditureForm(self.user, self.category, {
            'title': 'Grocery Shopping',
            'description': 'Weekly grocery shopping',
            'amount': 100.00,
            'date': datetime.date.today(),
            'otherCategory': -1,
        })
        expenditure = form.save(self.category)
        self.assertEqual(expenditure.title, 'Grocery Shopping')
        # Verify
        self.assertTrue(expenditure in self.category.expenditures.all())
    
    '''
    This test checks whether the form can successfully update an existing expenditure instance
    and verifies that the updated fields are correct 
    '''
    def testFormUpdate(self):
        form = ExpenditureForm(self.user, self.category, instance=self.expenditure, data={
            'title': 'Updated Title',
            'description': 'Updated Description',
            'amount': 200.00,
            'date': datetime.date.today(),
            'otherCategory': -1,
        })
        self.assertTrue(form.is_valid())
        updated_expenditure = form.save(self.category)
        # Verify
        self.assertEqual(updated_expenditure.title, 'Updated Title')
        self.assertEqual(updated_expenditure.description, 'Updated Description')
        self.assertEqual(updated_expenditure.amount, 200)
        self.assertEqual(updated_expenditure.date, datetime.date.today())
