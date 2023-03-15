from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure
import datetime

#tests for the category view

class CategoryViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.expenditure.date = datetime.datetime.now()
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)

    # This test ensures that the category view returns a 
    # 200 status code and uses the correct template.
    # 
    #  It also checks that the view returns the expected 
    # context variables (i.e. the category and its associated expenditures).
    def testCategoryViewGet(self):
        url = reverse('category', args=[self.category.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category.html')

        context = response.context
        self.assertEqual(context['category'], self.category)
        self.assertEqual(len(context['expenditures']), 1)
        self.assertEqual(context['expenditures'][0], self.expenditure)
    
    # This test ensures that if a user is not logged in and tries to
    # access the category view, they will be redirected to the login page.
    # 
    #  It checks that the view returns a 302 status code and redirects 
    # to the login page. It also checks that the login template is used.
    def testCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('category', kwargs={'categoryId': self.category.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')

    def testCategoryViewPagination(self):
        for i in range(15):
            expenditure = Expenditure.objects.create(title='testexpenditure' + str(i), date=datetime.date.today(), amount=10)
            self.category.expenditures.add(expenditure)
        # Check only 15 expenditures are displayed per page
        response = self.client.get(reverse('category', args=[self.category.id]))
        self.assertEqual(len(response.context['expenditures']), 10)
        # Check the next page displays the remaining 5 expenditures
        response = self.client.get(reverse('category', args=[self.category.id]) + '?page=2')
        self.assertEqual(len(response.context['expenditures']), 6)