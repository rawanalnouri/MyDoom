# Tests for the edit category view

from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, SpendingLimit
from ExpenseTracker.forms import CategorySpendingLimitForm
from django.contrib.messages import get_messages

class EditCategoryViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)


    # Verifies that the Edit Category view can be accessed and displays the correct form.
    def testGetEditCategoryView(self):
        url = reverse('editCategory', kwargs={'categoryId': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], CategorySpendingLimitForm)

    #  Tests if a valid form is submitted for editing a category and it is updated successfully.
    def testPostEditCategoryWhenFormIsValid(self):
        data = {
            'name': 'Updated Title', 
            'description': 'Updated Description', 
            'timePeriod': 'monthly', 
            'amount': 100 
        }
        response = self.client.post(reverse('editCategory', args=[self.category.id]), data, follow=True)
        self.assertRedirects(response, '/category/1/')
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Category updated successfully."
        self.assertEqual(str(messages[0]), expectedMessage)


    # Tests if an invalid form is submitted for editing a category and the update fails with an appropriate message.
    def testPostEditCategoryWhenFormIsInvalid(self):
        data = {
            'name': '', 
            'description': 'Updated Description', 
            'timePeriod': 'monthly', 
            'amount': -1
        }
        response = self.client.post(reverse('editCategory', args=[self.category.id]), data)
        self.assertRedirects(response, reverse('category', args=[self.category.id]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        expectedMessage = "Failed to update category."
        self.assertEqual(str(messages[0]), expectedMessage)
    
    # Verifies that the user is redirected to the login page if they are not logged in while accessing the Edit Category view.
    def testEditCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('editCategory', kwargs={'categoryId': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')


    # This test checks that when a user tries to edit a category and enters a name 
    # that already exists for the same user, an error message is displayed and the category is not updated.
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