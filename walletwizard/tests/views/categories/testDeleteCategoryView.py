"""Tests for delete category view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User, Category, Expenditure, SpendingLimit
from walletwizard.tests.testHelpers import reverse_with_next

class DeleteCategoryViewTest(TestCase):
    """Tests for delete category view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.spendingLimit = SpendingLimit.objects.get(id=1)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.users.add(self.user)
        self.category.expenditures.add(self.expenditure)
        self.url = reverse('deleteCategory', args=[self.category.id])

    def testDeleteCategoryViewGetDeletesCategoryAndItsAssociatedObjects(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SpendingLimit.objects.filter(id=self.spendingLimit.id).exists())
        self.assertFalse(Expenditure.objects.filter(id=self.expenditure.id).exists())
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def testRedirectsToHomeAfterDelete(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your category \'testcategory\' was successfully deleted.")

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')