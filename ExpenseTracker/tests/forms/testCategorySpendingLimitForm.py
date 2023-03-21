''' Tests for form handling the creation of categories'''

from django.test import TestCase
from django import forms
from ExpenseTracker.models import Category, User
from ExpenseTracker.forms import CategorySpendingLimitForm

class CategorySpendingLimitFormTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    # Defines data dictionary which represents a valid form submission for creating a category
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.data = {
            'name': 'Food',
            'description': 'This is a test category',
            'timePeriod': 'daily',
            'amount': 10
        }
    
    # This test checks the form has expected fields and widgets
    def testFormHasCorrectFieldsAndWidgets(self):   
        form = CategorySpendingLimitForm(user=self.user)
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('timePeriod', form.fields)
        self.assertIn('amount', form.fields)
        self.assertIsInstance(form.fields['timePeriod'].widget, forms.Select)
        self.assertIsInstance(form.fields['amount'].widget, forms.NumberInput)

    # This test checks the form can be validated with valid data
    def testFormValidation(self):
        form = CategorySpendingLimitForm(data=self.data, user=self.user)
        self.assertTrue(form.is_valid())
    
    # This test checks the form is not valid when required fields are missing
    def testFormValidationMissingFields(self):
        form = CategorySpendingLimitForm({
            'name': '',
            'description': '',
            'timePeriod': '',
            'amount': ''
        }, user=self.user)
        self.assertFalse(form.is_valid())

    # This test checks the form can be saved and the Category object has expected attributes
    def testFormSave(self):
        form = CategorySpendingLimitForm(data=self.data, user=self.user)
        self.assertTrue(form.is_valid())
        category = form.save()
        self.assertEqual(category.name, 'Food')
        self.assertEqual(category.description, 'This is a test category')
        self.assertTrue(self.user in self.category.users.all())
        self.assertEqual(category.spendingLimit.timePeriod, 'daily')
        self.assertEqual(category.spendingLimit.amount, 10)

    ''' 
    This test checks the form can be used to update the existing Category object 
    and that the resulting object has expected attributes 
    '''
    def testFormUpdate(self):
        form = CategorySpendingLimitForm(data=self.data, instance=self.category, user=self.user)
        form.is_valid()
        category = form.save()
        self.assertEqual(category.name, 'Food')
        self.assertEqual(category.description, 'This is a test category')
        self.assertTrue(self.user in self.category.users.all())
        self.assertEqual(category.spendingLimit.timePeriod, 'daily')
        self.assertEqual(category.spendingLimit.amount, 10)
    
    # This test checks that form prevents users from creating two categories with the same name
    def testFormCleanPreventsUserFromCreatingTwoCategoriesWithSameName(self):
        form = CategorySpendingLimitForm(data=self.data, user=self.user)
        self.assertTrue(form.is_valid())
        cleanedData = form.clean()
        self.assertEqual(cleanedData['name'], 'Food')
        self.assertEqual(cleanedData['description'], 'This is a test category')
        self.assertEqual(cleanedData['timePeriod'], 'daily')
        self.assertEqual(cleanedData['amount'], 10)

        # checks two categories with the same name cannot be created
        self.data['name'] = 'testcategory'
        form2 = CategorySpendingLimitForm(data=self.data, user=self.user)
        self.assertFalse(form2.is_valid())
        with self.assertRaisesMessage(forms.ValidationError, 
                'Category with this name already exists for this user.', 
                code='invalid'
            ):
            form2.clean()

    # This test checks users can't create a category with a spending limit that exceeds their overall spending limit.
    def testFormCleanPreventsUserFromCreatingCategoryIfSpendingLimitIsTooHigh(self):
        # Check category with low spending limit can be created
        form = CategorySpendingLimitForm(data=self.data, user=self.user)
        self.assertTrue(form.is_valid())
        cleanedData = form.clean()
        self.assertEqual(cleanedData['name'], 'Food')
        self.assertEqual(cleanedData['description'], 'This is a test category')
        self.assertEqual(cleanedData['timePeriod'], 'daily')
        self.assertEqual(cleanedData['amount'], 10)
        # Check category with high spending limit cannot be created
        self.data['name'] = 'Home'
        self.data['amount'] = 200
        self.assertEqual(self.user.overallSpendingLimit.timePeriod, self.data['timePeriod'])
        self.assertLess(self.user.overallSpendingLimit.amount, self.data['amount'])
        form2 = CategorySpendingLimitForm(data=self.data, user=self.user)
        self.assertFalse(form2.is_valid())
        with self.assertRaisesMessage(forms.ValidationError, 
            'The amount you\'ve chosen for this category\'s spending limit is too high '
            'compared to your overall spending limit.', 
            code='invalid'
            ):
            form2.clean()
            