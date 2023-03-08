from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure
from ExpenseTracker.forms import ExpenditureForm
import datetime

class CreateExpenditureViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.user.categories.add(self.category)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category.expenditures.add(self.expenditure)
        self.url = reverse('createExpenditure', kwargs={'categoryId': self.category.id})

    def test_get_create_expenditure_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], ExpenditureForm)

    def testCreateExpenditureViewWhenFormIsValid(self):
        data = {
            'title': 'testexpenditure2', 
            'date': datetime.date.today(), 
            'amount': 10
        }
        response = self.client.post(reverse('createExpenditure', args=[self.category.id]), data, follow=True)
        self.assertRedirects(response, '/category/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expenditure.objects.count(), 2)
        self.assertTrue(Expenditure.objects.filter(title='testexpenditure2').exists())
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Expenditure created successfully."
        self.assertEqual(str(messages[0]), expectedMessage)
    
    def testCreateExpenditureViewWhenFormIsInvalid(self):
        data = {
            'title': '', 
            'date': '', 
            'amount': -1
        }
        response = self.client.post(reverse('createExpenditure', args=[self.category.id]), data)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Failed to create expenditure."
        self.assertEqual(str(messages[0]), expectedMessage)
        self.assertEqual(Expenditure.objects.count(), 1)
        self.assertEqual(Expenditure.objects.first().title, 'testexpenditure')

    def testEditCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('createExpenditure', kwargs={'categoryId': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')