'''Unit tests of the expenditure form.'''
from django.test import TestCase
from django import forms
from walletwizard.forms import ExpenditureForm
from walletwizard.models import Expenditure, Category, SpendingLimit, User
import datetime

class ExpenditureFormTest(TestCase):
    '''Unit tests of the expenditure form.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.expenditure = Expenditure.objects.get(id=1) 
        self.formInput = {
            'title': 'Grocery Shopping',
            'description': 'Peas and beans',
            'amount': 50.00,
            'date': datetime.date.today(),
            'otherCategory': -1
        }
        self.category.expenditures.add(self.expenditure)
    
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

    def testFormValidation(self):
        form = ExpenditureForm(self.user, self.category, self.formInput)
        self.assertTrue(form.is_valid())

    def testFormValidationMissingFields(self):
        self.formInput['title'] = ''
        self.formInput['description'] = ''
        self.formInput['amount'] = ''
        self.formInput['date'] = ''
        self.formInput['otherCategory'] = ''
        form = ExpenditureForm(self.user, self.category, self.formInput)
        self.assertFalse(form.is_valid())

    def testFormSave(self):
        form = ExpenditureForm(self.user, self.category, self.formInput)
        expenditure = form.save(self.category)
        self.assertEqual(expenditure.title, 'Grocery Shopping')
        self.assertTrue(expenditure in self.category.expenditures.all())
    
    def testFormUpdate(self):
        form = ExpenditureForm(self.user, self.category, instance=self.expenditure, data=self.formInput)
        self.assertTrue(form.is_valid())
        updatedExpenditure = form.save(self.category)
        self.assertEqual(updatedExpenditure.title, 'Grocery Shopping')
        self.assertEqual(updatedExpenditure.description, 'Peas and beans')
        self.assertEqual(updatedExpenditure.amount, 50)
        self.assertEqual(updatedExpenditure.date, datetime.date.today())