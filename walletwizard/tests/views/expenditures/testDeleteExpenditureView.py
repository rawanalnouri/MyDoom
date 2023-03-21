"""Tests of delete expenditure view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import User, Category, Expenditure
from walletwizard.tests.testHelpers import reverse_with_next

class DeleteExpenditureViewTest(TestCase):
    """Tests of delete expenditure view."""
    
    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.expenditure = Expenditure.objects.get(id=1)
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.expenditures.add(self.expenditure)
        self.url = reverse('deleteExpenditure', args=[self.category.id, self.expenditure.id])
        
    def testDeleteExpenditureView(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Expenditure.objects.filter(id=self.expenditure.id).exists())

    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')