from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure
from ExpenseTracker.forms import CategorySpendingLimitForm
import datetime

#tests for the edit category view


class EditCategoryViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)


    # Verifies that the Edit Category view can be accessed 
    # and displays the correct form.
    def testGetEditCategoryView(self):
        url = reverse('editCategory', kwargs={'categoryId': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], CategorySpendingLimitForm)

    #  Tests if a valid form is submitted for editing a category
    #  and it is updated successfully.
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


    # Tests if an invalid form is submitted for editing a category 
    # and the update fails with an appropriate message.
    def testPostEditCategoryWhenFormIsInvalid(self):
        data = {
            'name': '', 
            'description': 'Updated Description', 
            'timePeriod': 'monthly', 
            'amount': -1
        }
        response = self.client.post(reverse('editCategory', args=[self.category.id]), data)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Failed to update category."
        self.assertEqual(str(messages[0]), expectedMessage)
    
    # Verifies that the user is redirected to the login page if they 
    # are not logged in while accessing the Edit Category view.
    def testEditCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('editCategory', kwargs={'categoryId': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')

    # Tests that pagination is working correctly for the Category view, 
    # and that only the correct number of expenditures are displayed on each page.
    def testCategoryViewPagination(self):
        # Create additional expenditures
        for i in range(15):
            expenditure = Expenditure.objects.create(title='testexpenditure' + str(i), date=datetime.date.today(), amount=10)
            self.category.expenditures.add(expenditure)
        # Check only 15 expenditures are displayed per page
        response = self.client.get(reverse('category', args=[self.category.id]))
        self.assertEqual(len(response.context['expenditures']), 10)
        # Check the next page displays the remaining 5 expenditures
        response = self.client.get(reverse('category', args=[self.category.id]) + '?page=2')
        self.assertEqual(len(response.context['expenditures']), 5)