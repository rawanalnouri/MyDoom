from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.forms import ReportForm
from ExpenseTracker.models import *
import datetime


class ReportViewTest(TestCase):


    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']


    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)

        self.expenditure = Expenditure.objects.get(id=1)
        self.expenditure.date = datetime.datetime.now()
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)



#  testing if page is correctly loaded
# with the correct form
# and with the correct template
    def testCategoryReportViewGet(self):
        url = reverse('reports')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports.html')
        self.assertIsInstance(response.context['form'], ReportForm)


    def testReportsViewRedirectsToLoginIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('reports')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')

    def testCategoryTimeFilters(self):
        for i in range(15):
            expenditure = Expenditure.objects.create(title='testexpenditure' + str(i), date=datetime.date.today(), amount=10)
            self.category.expenditures.add(expenditure)
        response = self.client.get(reverse('category', args=[self.category.id]))
        self.assertEqual(len(response.context['expenditures']), 10)
        # create_posts(other_user, 100, 103)
        # create_posts(self.user, 200, 203)
        # response = self.client.get(self.url)
        # for count in range(100, 103):
        #     self.assertNotContains(response, f'Post__{count}')
        # for count in range(200, 203):
        #     self.assertContains(response, f'Post__{count}')
