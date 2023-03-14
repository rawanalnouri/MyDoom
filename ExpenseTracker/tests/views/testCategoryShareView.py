from ExpenseTracker.models import User, Category
from ExpenseTracker.forms import ShareCategoryForm
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages

#tests for the share category view


class CategroyShareViewTest(TestCase):
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


    # tests whether the URL for sharing a category is correct.
    def testUrl(self):
        self.assertEqual('/shareCategory/1/', self.url)

    # tests whether the share category form is rendered correctly 
    # and the expected form is used.
    def testCategoryShareViewGet(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        shareCategoryForm = response.context['form']
        self.assertTrue(isinstance(shareCategoryForm,ShareCategoryForm))

    # tests whether an unsuccessful attempt to share a category 
    # results in the correct error message being displayed to the user.
    def testUnsuccessfulShareCategory(self):
        data = {'user': ''}
        response = self.client.post(reverse('shareCategory', args=[self.category.id]), data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Failed to send share category request "
        self.assertEqual(str(messages[0]), expectedMessage)

    # tests whether a successful attempt to share a category 
    # results in the correct success message being displayed to the 
    # user and whether the user is redirected to the correct page.
    def testSuccessfulShareCategory(self):
        data = {'user': self.userToShareCategoryWith.pk}
        response = self.client.post(reverse('shareCategory', args=[self.category.id]), data, follow=True)
        self.assertRedirects(response, '/category/1/')
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Successfully sent request to share '"+ self.category.name +"' with "+ self.userToShareCategoryWith.username
        self.assertEqual(str(messages[0]), expectedMessage)


    #  tests whether a user who is not logged in is redirected 
    # to the login page when attempting to share a category.
    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('shareCategory', args=[self.category.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')


    

        




