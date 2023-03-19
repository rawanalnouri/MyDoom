from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, SpendingLimit, Category, Points
from ExpenseTracker.forms import OverallSpendingForm

class SetOverallSpendingLimitViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']
    
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        
    def testGet(self):
        response = self.client.get(reverse('setOverallSpendingLimit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        form = response.context['form']
        self.assertIsInstance(form, OverallSpendingForm)
        
    def testPostValidFormExistingLimit(self):
        data = {'timePeriod': 'weekly', 'amount': 300}
        response = self.client.post(reverse('setOverallSpendingLimit'), data=data)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.user.overallSpendingLimit.amount, 300)
        
    def testPostValidFormNoExistingLimit(self):
        self.client.logout()
        secondUser = User.objects.create_user(
            username='janedoe', 
            email='janedoe@example.org', 
            firstName='Jane',
            lastName='Doe',
            password='Password123',
        )
        Points.objects.create(
            count = 50,
            user = secondUser
        )
        category = Category.objects.get(id=1)
        secondUser.categories.add(category)
        category.users.add(secondUser)
        self.client.force_login(secondUser)
        data = {'timePeriod': 'daily', 'amount': 400}
        response = self.client.post(reverse('setOverallSpendingLimit'), data=data)
        self.assertRedirects(response, reverse('home'))
        self.assertIsNotNone(self.user.overallSpendingLimit)
        
    def testPostInvalidFormWithAmountEqualToZero(self):
        self.user.overallSpendingLimit = None
        data = {'timePeriod': 'monthly', 'amount': 0}
        response = self.client.post(reverse('setOverallSpendingLimit'), data=data, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.user.overallSpendingLimit, None)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Failed to update overall spending limit.')

    def testPostInvalidFormWithAmountTooLow(self):
        self.user.overallSpendingLimit = None
        data = {'timePeriod': 'daily', 'amount': 10}
        response = self.client.post(reverse('setOverallSpendingLimit'), data=data, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.user.overallSpendingLimit, None)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your overall spending limit is too low compared to the spending limits set in your categories.')
    
    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('setOverallSpendingLimit')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')