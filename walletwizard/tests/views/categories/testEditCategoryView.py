"""Tests of edit category view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User, Category, SpendingLimit
from walletwizard.forms import CategorySpendingLimitForm
from django.contrib.messages import get_messages
from walletwizard.tests.testHelpers import reverse_with_next

class EditCategoryViewTest(TestCase):
    """Tests of edit category view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.user.categories.add(self.category)
        self.category.save()
        self.formInput = {
            'name': 'updatedCategory',
            'description': 'This is a test category.',
            'timePeriod': 'monthly', 
            'amount': 100
        }
        self.url = reverse('editCategory', args=[self.category.id])

    def testGetEditCategoryView(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], CategorySpendingLimitForm)

    def testPostEditCategoryWhenFormIsValid(self):
        response = self.client.post(self.url, self.formInput, follow=True)
        self.assertRedirects(response, '/category/1/')
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Your category 'updatedCategory' was updated successfully."
        self.assertEqual(str(messages[0]), expectedMessage)

    def testPostEditCategoryWhenFormIsInvalid(self):
        self.formInput['name'] = ''
        self.formInput['amount'] = -1
        response = self.client.post(self.url, self.formInput)
        self.assertRedirects(response, reverse('category', args=[self.category.id]))
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        expectedMessage = "Failed to update category."
        self.assertEqual(str(messages[0]), expectedMessage)

    def testEditCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')

    def testEditCategoryViewSameNameError(self):
        newSpendingLimit = SpendingLimit.objects.create(timePeriod='weekly', amount=10)
        newCategory = Category.objects.create(
            name='sameName', 
            description='This is another test category', 
            spendingLimit=newSpendingLimit
        )
        newCategory.users.add(self.user)
        self.user.categories.add(newCategory)
        self.formInput['name'] = 'sameName'
        response = self.client.post(self.url, data=self.formInput)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category', args=[self.category.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Category with this name already exists for this user.")
        self.assertEqual(messages[0].level_tag, "danger")

    def testEditCategoryViewWithAmountTooHigh(self):
        self.formInput['amount'] = 200
        self.formInput['timePeriod'] = 'daily'
        response = self.client.post(self.url, data=self.formInput, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('category', args=[self.category.id]))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The amount you\'ve chosen for this category\'s spending limit is too'
            ' high compared to your overall spending limit.'
        )
        self.assertEqual(messages[0].level_tag, "danger")