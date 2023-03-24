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
        
    def testDeleteExpenditureViewGetDeletesOnlyTheExpenditure(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Expenditure.objects.filter(id=self.expenditure.id).exists())
        self.assertTrue(Category.objects.filter(id=self.category.id).exists())
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def testRedirectsToCategoryViewAfterDelete(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        userRedirect = reverse('category', args=[self.category.id])
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'category.html')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your expenditure \'testexpenditure\' was successfully deleted.")

    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')