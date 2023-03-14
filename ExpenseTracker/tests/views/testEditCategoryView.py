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

    def testGetEditCategoryView(self):
        url = reverse('editCategory', kwargs={'categoryId': self.category.id})
        response = self.client.get(url)
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
        response = self.client.post(reverse('editCategory', args=[self.category.id]), data, follow=True)
        self.assertRedirects(response, '/category/1/')
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Category updated successfully."
        self.assertEqual(str(messages[0]), expectedMessage)

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
        
    def testEditCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('editCategory', kwargs={'categoryId': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')
    
    def testEditCategoryViewSameNameError(self):
        newSpendingLimit = SpendingLimit.objects.create(timePeriod='weekly', amount=10)
        newCategory = Category.objects.create(name='Food', description='This is another test category', spendingLimit=newSpendingLimit)
        newCategory.users.add(self.user)
        # Create a post request data with the same name as the existing category
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