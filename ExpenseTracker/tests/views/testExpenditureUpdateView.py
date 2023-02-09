from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, SpendingLimit
from ExpenseTracker.forms import ExpenditureForm
import datetime

class ExpenditureUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.create(title='testexpenditure', date=datetime.date.today(), amount=10, mood='content')
        spendingLimit = SpendingLimit.objects.create(amount='20', timePeriod='daily')
        self.category = Category.objects.create(name='testcategory', spendingLimit=spendingLimit, user=self.user)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
    
    def testGetMethod(self):
        response = self.client.get(reverse('updateExpenditure', kwargs={'categoryName': self.category.name, 'expenditureId': self.expenditure.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], ExpenditureForm)
        self.assertEqual(response.context['form'].instance, self.expenditure)

    def testPostMethodValidData(self):
        self.url = reverse('updateExpenditure', args=[self.category.name, self.expenditure.id])
        response = self.client.post(self.url, data={
            'title': 'Updated Title',
            'description': 'Updated Description',
            'amount': 200.00,
            'date': datetime.date.today(),
            'mood': 'happy'
        })
        updated_expenditure = Expenditure.objects.get(id=self.expenditure.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('category', args=[self.category.name]))
        self.assertEqual(updated_expenditure.title, 'Updated Title')
        self.assertEqual(updated_expenditure.description, 'Updated Description')
        self.assertEqual(updated_expenditure.amount, 200.00)
        self.assertEqual(updated_expenditure.mood, 'happy')
        
    def testPostMethodWithInvalidData(self):
        response = self.client.post(reverse('updateExpenditure', kwargs={'categoryName': self.category.name, 'expenditureId': self.expenditure.id}), data={
            'title': '',
            'description': '',
            'amount': '',
            'date': '',
            'mood': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], ExpenditureForm)
        self.assertFalse(response.context['form'].is_valid())
        self.assertContains(response, 'This field is required')