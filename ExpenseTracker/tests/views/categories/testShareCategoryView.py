"""Tests for share category view."""
from ExpenseTracker.models import User, Category
from ExpenseTracker.forms import ShareCategoryForm
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.tests.testHelpers import reverse_with_next

class CategroyShareViewTest(TestCase):
    """Tests for share category view."""

    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.category = Category.objects.get(id=1)
        self.url = reverse('shareCategory', args=[self.category.id])

        self.userToShareCategoryWith = User.objects.create(
            username = "9lucy",
            firstName = "lucy",
            lastName = "green",
            email = "lucygreen@email.com", 
            password = "Password123" 
        )
        self.user.followers.add(self.userToShareCategoryWith)
        self.userToShareCategoryWith.followers.add(self.user)

    def testUrl(self):
        self.assertEqual('/shareCategory/1/', self.url)

    def testShareCategoryViewGet(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        shareCategoryForm = response.context['form']
        self.assertTrue(isinstance(shareCategoryForm,ShareCategoryForm))

    def testUnsuccessfulShareCategory(self):
        data = {'user': ''}
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Failed to send share category request."
        self.assertEqual(str(messages[0]), expectedMessage)

    def testUnsuccessfulShareOfCategoryWithSameName(self):
        self.userToShareCategoryWith.categories.add(self.category)
        self.userToShareCategoryWith.save()
        data = {'user': self.userToShareCategoryWith.pk}
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = 'The user you want to share this category with already has a category with the same name.\nChange the name of the category before sharing.'
        self.assertEqual(str(messages[0]), expectedMessage)

    def testSuccessfulShareCategory(self):
        data = {'user': self.userToShareCategoryWith.pk}
        response = self.client.post(self.url, data, follow=True)
        self.assertRedirects(response, '/category/1/')
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "A request to share category 'testcategory' has been sent to '9lucy'."
        self.assertEqual(str(messages[0]), expectedMessage)

    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')