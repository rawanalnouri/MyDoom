"""Tests of edit expenditure view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User, Category, Expenditure, SpendingLimit
from walletwizard.forms import ExpenditureForm
from walletwizard.tests.testHelpers import reverse_with_next
import datetime

class EditExpenditureViewTest(TestCase):
    """Tests of edit expenditure view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']
    
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
        self.formInput = {
            'title': 'updatedExpenditure',
            'description': 'This is a test expenditure.',
            'amount': 200.00,
            'date': datetime.date.today(),
            'receipt': '',
            'otherCategory': -1,
        }
        self.url = reverse('editExpenditure', args=[self.category.id, self.expenditure.id])
    
    def testGetEditExpenditureView(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], ExpenditureForm)
        self.assertEqual(response.context['form'].instance, self.expenditure)

    def testPostMethodValidData(self):
        response = self.client.post(self.url, data=self.formInput)
        updatedExpenditure = Expenditure.objects.get(id=self.expenditure.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', args=[self.category.id]))
        self.assertEqual(updatedExpenditure.title, 'updatedExpenditure')
        self.assertEqual(updatedExpenditure.description, 'This is a test expenditure.')
        self.assertEqual(updatedExpenditure.amount, 200.00)

    def testPostMethodWithInvalidData(self):
        self.formInput['title'] = '',
        self.formInput['description'] = '',
        self.formInput['amount'] = '',
        self.formInput['date'] = '',
        self.formInput['otherCategory'] = -1
        response = self.client.post(self.url, data=self.formInput, follow=True) 
        redirectUrl =  reverse('category', args=[self.category.id])
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, redirectUrl)
        self.assertTemplateUsed(response, 'category.html')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 3)

    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')

    def testExpenditureIsSharedWithCorrectCategory(self):
        category2 = Category.objects.create(
            name = "notUpdatedCategory",
            spendingLimit = SpendingLimit.objects.get(id=1)
        )
        category2.users.add(self.user)
        category2.save()
        self.user.categories.add(category2)
        expendituresBefore = category2.expenditures.count()
        self.formInput['otherCategory'] = 2
        response = self.client.post(self.url, data=self.formInput)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', args=[self.category.id]))
        expendituresAfter = category2.expenditures.count()
        expenditureAdded = category2.expenditures.first()
        self.assertEqual(expendituresAfter, expendituresBefore+1)
        self.assertEqual(expenditureAdded.title, 'updatedExpenditure')
        self.assertEqual(expenditureAdded.description, 'This is a test expenditure.')
        self.assertEqual(expenditureAdded.amount, 200.00)