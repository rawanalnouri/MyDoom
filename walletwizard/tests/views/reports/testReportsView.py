"""Tests for the reports view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.tests.testHelpers import reverse_with_next
from walletwizard.forms import ReportForm
from walletwizard.models import User, Expenditure, Category
import datetime

class ReportViewTest(TestCase):
    """Tests for the reports view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.url = reverse('reports')

        self.expenditure = Expenditure.objects.get(id=1)
        self.expenditure.date = datetime.datetime.now()
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.user.save()
        self.category.users.add(self.user)
        self.category.expenditures.add(self.expenditure)
        self.category.save()
        self.input = {
            "timePeriod": "month",
            "selectedCategory": self.category.id
        }
        self.form = ReportForm(user=self.user, data=input)

    def testReportsUrl(self):
        self.assertEqual(self.url,'/reports/')

    def testReportsViewGet(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports.html')
        self.assertIsInstance(response.context['form'], ReportForm)
    
    def testRedirectsToLogInIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')

    def testPostWithValidFormData(self):
        response = self.client.post(reverse('reports'), self.input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('reports.html')
        self.assertIsInstance(response.context['form'], ReportForm)

    def testPostWithInvalidFormData(self):
        self.input['selectedCategory'] = ''
        response = self.client.post(reverse('reports'), self.input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('reports.html')
        self.assertEqual(response.context['labels'], [])
        self.assertEqual(response.context['data'], [])