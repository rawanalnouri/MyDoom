"""Tests for set overall spending limit view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User, Category, Points
from walletwizard.forms import OverallSpendingForm
from walletwizard.tests.testHelpers import reverse_with_next

class SetOverallSpendingLimitViewTest(TestCase):
    """Tests for set overall spending limit view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']
    
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.url = reverse('setOverallSpendingLimit')
        self.formInput = {'timePeriod': 'weekly', 'amount': 300}
    
    def testGet(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        form = response.context['form']
        self.assertIsInstance(form, OverallSpendingForm)
        
    def testPostValidFormExistingLimit(self):
        response = self.client.post(self.url, data=self.formInput)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.user.overallSpendingLimit.amount, 300)
        
    def testPostWhenSpendingLimitIsNoneIsSuccessful(self):
        self.client.logout()
        secondUser = User.objects.create_user(
            username='janedoe', 
            email='janedoe@example.org', 
            firstName='Jane',
            lastName='Doe',
            password='Password123',
        )
        Points.objects.create(count = 50, user = secondUser)
        category = Category.objects.get(id=1)
        secondUser.categories.add(category)
        category.users.add(secondUser)
        self.client.force_login(secondUser)
        response = self.client.post(self.url, data=self.formInput)
        self.assertRedirects(response, reverse('home'))
        self.assertIsNotNone(self.user.overallSpendingLimit)
        
    def testPostWhenFormInputIsBlankIsUnsuccessful(self):
        self.user.overallSpendingLimit = None
        self.formInput['timePeriod'] = ''
        self.formInput['amount'] = ''
        response = self.client.post(self.url, data=self.formInput, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.user.overallSpendingLimit, None)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Failed to update overall spending limit.')
        
    def testPostWhenAmountIsEqualToZeroIsUnsuccessful(self):
        self.user.overallSpendingLimit = None
        self.formInput['amount'] = 0
        response = self.client.post(self.url, data=self.formInput, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.user.overallSpendingLimit, None)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Failed to update overall spending limit.')

    def testPostWhenAmountIsTooLowIsUnsuccessful(self):
        category = Category.objects.get(id=1)
        self.user.categories.add(category)
        category.users.add(self.user)
        self.user.overallSpendingLimit = None
        self.formInput['timePeriod'] = 'daily'
        self.formInput['amount'] = 10
        response = self.client.post(self.url, data=self.formInput, follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.user.overallSpendingLimit, None)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your overall spending limit is too low compared to the spending limits set in your categories.')
    
    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')