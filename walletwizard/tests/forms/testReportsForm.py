'''Unit tests of reports form.'''
from django import forms
from django.test import TestCase
from walletwizard.forms import ReportForm, TIME_PERIOD_CHOICES
from walletwizard.models import User, Category

class ReportsFormTest(TestCase):
    '''Unit tests of reports form.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(username='testuser')
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.category.save()
        self.user.categories.add(self.category)
        self.user.save()
        self.client.force_login(self.user)
        self.input = {
            "timePeriod": "month",
            "selectedCategory": [self.category.id]
        }

    def testFormContainsCorrectFields(self):
        form = ReportForm(user=self.user, data=self.input)
        self.assertIn('timePeriod', form.fields)
        self.assertIn('selectedCategory', form.fields)
        self.assertTrue(form.fields['timePeriod'], forms.ChoiceField)
        self.assertTrue(form.fields['selectedCategory'], forms.MultipleChoiceField)

    def testFormAcceptsValidInput(self):
        form = ReportForm(user=self.user, data=self.input)
        self.assertTrue(form.is_valid())
    
    def testFormDoesNotAcceptInvalidTimePeriod(self):
        self.input['timePeriod']= 'invalid'
        form = ReportForm(user=self.user, data=self.input)
        self.assertFalse(form.is_valid())
        self.assertIn('timePeriod', form.errors)

    def testFormDoesNotAcceptInvalidCategory(self):
        self.input['selectedCategory'] = 7
        form = ReportForm(user=self.user, data=self.input)
        self.assertFalse(form.is_valid())
        self.assertIn('selectedCategory', form.errors)

    def testFormHasCorrectInitialData(self):
        form = ReportForm(user=self.user)
        self.assertEqual(form.fields['timePeriod'].choices, TIME_PERIOD_CHOICES)
        categoryChoices = [(self.category.id, self.category)]
        self.assertEqual(form.fields['selectedCategory'].choices, categoryChoices)

    def testFormDisplaysCorrectCategoryOptions(self):
        form = ReportForm(user=self.user, data=self.input)
        options = form.createCategorySelection()
        self.assertEqual(options[0][0], self.category.id)
        self.assertEqual(options[0][1], self.category)