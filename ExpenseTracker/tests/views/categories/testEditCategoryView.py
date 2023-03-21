"""Tests of edit category view."""
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, SpendingLimit
from ExpenseTracker.forms import CategorySpendingLimitForm
from django.contrib.messages import get_messages
from ExpenseTracker.tests.testHelpers import reverse_with_next

class EditCategoryViewTest(TestCase):
    """Tests of edit category view."""

    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.category.save()
        self.url = reverse('editCategory', args=[self.category.id])

    def testGetEditCategoryView(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], CategorySpendingLimitForm)

    def testPostEditCategoryWhenFormIsValid(self):
        data = {
            'name': 'Updated Title', 
            'description': 'Updated Description', 
            'timePeriod': 'monthly', 
            'amount': 100 
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertRedirects(response, '/category/1/')
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Your category 'Updated Title' was updated successfully."
        self.assertEqual(str(messages[0]), expectedMessage)

    def testPostEditCategoryWhenFormIsInvalid(self):
        data = {
            'name': '', 
            'description': 'Updated Description', 
            'timePeriod': 'monthly', 
            'amount': -1
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response,  reverse('category', args=[self.category.id]))
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
        newCategory = Category.objects.create(name='Food', description='This is another test category', spendingLimit=newSpendingLimit)
        newCategory.users.add(self.user)
        # Create a post request data with the same name as the existing category.
        postData = {
            'name': 'testcategory',
            'description': 'This is an edited test category',
            'timePeriod': 'monthly',
            'amount': 20
        }
        response = self.client.post(reverse('editCategory', args=[newCategory.id]), data=postData)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category', args=[newCategory.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Category with this name already exists for this user.")
        self.assertEqual(messages[0].level_tag, "danger")