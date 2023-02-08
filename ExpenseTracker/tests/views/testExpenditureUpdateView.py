from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, SpendingLimit
from ExpenseTracker.forms import ExpenditureForm
import datetime

class ExpenditureUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.create(title='testexpenditure', date=datetime.date.today(), amount=10)
        spendingLimit = SpendingLimit.objects.create(amount='20', timePeriod='daily')
        self.category = Category.objects.create(name='testcategory', spendingLimit=spendingLimit, user=self.user)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
    
    def testGetRequest(self):
        response = self.client.get(reverse('updateExpenditure', kwargs={'categoryName': self.category.name, 'expenditureId': self.expenditure.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], ExpenditureForm)
        self.assertEqual(response.context['form'].instance, self.expenditure)

    # testPostRequest
        
    def testPostRequestWithInvalidData(self):
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