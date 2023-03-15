from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, SpendingLimit
from ExpenseTracker.forms import ExpenditureForm
import datetime

class ExpenditureUpdateViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']
    
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
    
    # def testGetMethod(self):
    #     response = self.client.get(reverse('updateExpenditure', kwargs={'categoryId': self.category.id, 'expenditureId': self.expenditure.id}))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
    #     self.assertIsInstance(response.context['form'], ExpenditureForm)
    #     self.assertEqual(response.context['form'].instance, self.expenditure)

    def testPostMethodValidData(self):
        self.url = reverse('updateExpenditure', args=[self.category.id, self.expenditure.id])
        response = self.client.post(self.url, data={
            'title': 'Updated Title',
            'description': 'Updated Description',
            'amount': 200.00,
            'date': datetime.date.today(),
            'receipt': ''
        })
        updated_expenditure = Expenditure.objects.get(id=self.expenditure.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', args=[self.category.id]))
        self.assertEqual(updated_expenditure.title, 'Updated Title')
        self.assertEqual(updated_expenditure.description, 'Updated Description')
        self.assertEqual(updated_expenditure.amount, 200.00)
        
    # def testPostMethodWithInvalidData(self):
    #     response = self.client.post(reverse('updateExpenditure', kwargs={'categoryId': self.category.id, 'expenditureId': self.expenditure.id}), data={
    #         'title': '',
    #         'description': '',
    #         'amount': '',
    #         'date': '',
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
    #     self.assertIsInstance(response.context['form'], ExpenditureForm)
    #     self.assertFalse(response.context['form'].is_valid())
    #     self.assertContains(response, 'This field is required')

    # def testRedirectsToLoginIfUserNotLoggedIn(self):
    #     self.client.logout()
    #     response = self.client.get(reverse('updateExpenditure', args=[self.category.id, self.expenditure.id]))
    #     self.assertRedirects(response, reverse('logIn'))