from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, SpendingLimit

#tests for the delete category view

class CategoryDeleteViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.spendingLimit = SpendingLimit.objects.get(id=1)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.users.add(self.user)
        self.category.expenditures.add(self.expenditure)

    # This test verifies that when a user deletes a category, 
    # the corresponding spending limit and expenditures are also 
    # deleted from the database.
    # 
    #  It checks that the objects no longer exist in the database.
    def testCategoryDeleteViewRemovesCategoryAndExpendituresAndSpendingLimit(self):
        self.client.get(reverse('deleteCategory', args=[self.category.id]))
        self.assertFalse(SpendingLimit.objects.filter(id=self.spendingLimit.id).exists())
        self.assertFalse(Expenditure.objects.filter(id=self.expenditure.id).exists())
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    # This test verifies that after deleting a category,
    # the user is redirected to the home page and that the home.html 
    # template is used to render the response.
    def testRedirectToHomeAfterDelete(self):
        response = self.client.get(reverse('deleteCategory', args=[self.category.id]), follow=True)
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    # This test verifies that a user who is not logged in is 
    # redirected to the login page if they try to delete a category.
    # 
    #  It checks that the response has a redirect status code and 
    # that the logIn.html template is used to render the response.
    def testRedirectsToLoginIfUserNotLoggedIn(self):
        self.client.logout()
        response = self.client.delete(reverse('deleteCategory', args=[self.category.id]))
        self.assertRedirects(response, reverse('logIn'))