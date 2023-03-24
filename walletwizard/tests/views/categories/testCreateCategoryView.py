"""Tests of create category view."""
from walletwizard.models import User, Category
from django.test import TestCase
from django.urls import reverse
from walletwizard.tests.testHelpers import reverse_with_next

class CreateCategoryViewTest(TestCase):
    """Tests of create category view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.formInput = {
            'name': 'Food',
            'description': 'This is a test category',
            'amount': 20,
            'timePeriod':'daily',
        }
        self.url = reverse('createCategory')

    def testCreateCategoryViewRedirectsToCategoryOnSuccess(self):
        response = self.client.post(self.url, self.formInput)
        category = Category.objects.get(name='Food')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category', args=[category.id]))

    def testCreateCategoryViewDisplaysErrorsOnFailure(self):
        self.formInput['name'] = ''
        response = self.client.post(self.url, self.formInput)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')

    def testCreateCategoryViewSameNameError(self):
        category = Category.objects.get(id=1)
        category.name = 'SameName'
        category.users.add(self.user)
        self.user.categories.add(category)
        category.save()
        self.formInput['name'] = 'SameName'
        response = self.client.post(self.url, data=self.formInput)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Category with this name already exists for this user.")
        self.assertEqual(messages[0].level_tag, "danger")

    def testPostInvalidFormWithAmountTooHigh(self):
        self.formInput['amount'] = 200
        response = self.client.post(self.url, data=self.formInput)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 
            'The amount you\'ve chosen for this category\'s spending limit is too'
            ' high compared to your overall spending limit.'
        )
    