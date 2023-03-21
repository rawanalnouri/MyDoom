"""Tests of create category view."""
from walletwizard.models import User, Category, SpendingLimit
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from walletwizard.tests.testHelpers import reverse_with_next

class CreateCategoryViewTest(TestCase):
    """Tests of create category view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.data = {
            'name': 'Food',
            'amount': 20,
            'timePeriod':'daily',
        }
        self.url = reverse('createCategory')

    def testCreateCategoryViewRedirectsToCategoryOnSuccess(self):
        response = self.client.post(self.url, self.data)
        category = Category.objects.get(name='Food')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category', args=[category.id]))

    def testCreateCategoryViewDisplaysErrorsOnFailure(self):
        self.data['name'] = ''
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')

    def testCreateCategoryViewSameNameError(self):
        spendingLimit = SpendingLimit.objects.create(timePeriod='weekly', amount=10)
        category = Category.objects.create(name='SameName', description='This is another test category', spendingLimit=spendingLimit)
        category.users.add(self.user)
         # Create a post request data with the same name as the existing category.
        postData = {
            'name': 'SameName',
            'description': 'This is a new test category',
            'timePeriod': 'daily',
            'amount': 5
        }
        response = self.client.post(self.url, data=postData)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Category with this name already exists for this user.")
        self.assertEqual(messages[0].level_tag, "danger")

    def testPostInvalidFormWithAmountTooHigh(self):
        self.user.overallSpendingLimit = None
        data = {'timePeriod': 'daily', 'amount': 200}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.overallSpendingLimit, None)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'The amount you\'ve chosen for this category\'s spending limit is too high compared to your overall spending limit.')
    