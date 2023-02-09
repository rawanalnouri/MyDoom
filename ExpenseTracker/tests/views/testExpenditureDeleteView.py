from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, SpendingLimit
import datetime

class ExpenditureDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@email.com', password='testpassword')
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.create(title='testexpenditure', date=datetime.date.today(), amount=10)
        spendingLimit = SpendingLimit.objects.create(amount='20', timePeriod='daily')
        self.category = Category.objects.create(name='testcategory', spendingLimit=spendingLimit, user=self.user)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
        
    def testExpenditureDeleteView(self):
        response = self.client.delete(reverse('deleteExpenditure', args=['testcategory', self.expenditure.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Expenditure.objects.filter(id=self.expenditure.id).exists())