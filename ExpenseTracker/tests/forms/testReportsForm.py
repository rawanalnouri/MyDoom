from django import forms
from django.test import TestCase
from ExpenseTracker.forms import ReportForm
from ExpenseTracker.models import *
from django.urls import reverse

class ReportsFormTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(username='bob123')
        self.client.force_login(self.user)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.category.save()
        self.user.categories.add(self.category)
        self.user.save()
        self.input = {
            "timePeriod": "month",
            "selectedCategory": "testcategory"
        }
        self.form = ReportForm(user=self.user, data=input)

    def testFormContainsCorrectFields(self):
        self.assertIn('timePeriod', self.form.fields)
        self.assertIn('selectedCategory', self.form.fields)
        self.assertTrue(self.form.fields['timePeriod'], forms.ChoiceField)
        self.assertTrue(self.form.fields['selectedCategory'], forms.MultipleChoiceField)

    def testFormDisplaysCorrectCategoryOptions(self):
        options = self.form.createCategorySelection()
        self.assertEqual(options[0][0], self.category.id)
        self.assertEqual(options[0][1], self.category)
