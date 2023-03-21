''' Tests for form handling categories being shared'''

from django.test import TestCase
from ExpenseTracker.models import User, Category, Notification
from ExpenseTracker.forms import ShareCategoryForm
from django.urls import reverse
from django import forms

class ShareCategoryFormTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    # Creates necessary objects and setup the test environment including two users, a 'Category', and the relationships between them
    def setUp(self):
        self.user = User.objects.get(id=1)
        self.secondUser = User.objects.create_user(
            username='janedoe', 
            email='janedoe@example.org', 
            firstName='Jane',
            lastName='Doe',
            password='Password123',
        )
        self.client.force_login(self.user)
        self.category = Category.objects.get(id=1)
        self.user.categories.add(self.category)
        self.category.users.add(self.user)

    # Tests the form with valid data
    # Checks that the shared category has been added to the new user's categories and the new user has been added to the shared category's user
    def testFormWithValidData(self):
        validUser = self.secondUser
        self.user.followers.add(validUser)
        # submit 'share category' form
        formData = {'user': validUser.id}
        form = ShareCategoryForm(fromUser=self.user, category=self.category, data=formData)
        self.assertTrue(form.is_valid())
        form.save()
        # accept 'share category' request
        notification = Notification.objects.filter(toUser=validUser).latest('createdAt')
        acceptUrl = reverse('acceptCategoryShare', args=[notification.id])
        response = self.client.get(acceptUrl)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(validUser in self.category.users.all())
        self.assertTrue(self.category in validUser.categories.all())

    # Tests the form with a user that already has a category with the same name as the shared category
    def testFromWithUserThatHasSameCategoryName(self):
        validUser = self.secondUser
        validUser.categories.add(self.category)
        validUser.save()
        self.user.followers.add(validUser)
        formData = {'user': validUser.id}
        form = ShareCategoryForm(fromUser=self.user, category=self.category, data=formData)
        self.assertFalse(form.is_valid())
        with self.assertRaisesMessage(forms.ValidationError, 
                'The user you want to share this category with already has a category with the same name.\\n'
                +'Change the name of the category before sharing.', code='invalid'
            ):
            form.clean()

    # Tests the form with an invalid user ID, checks that the form is not valid and has an error for the user field
    def testFormWithInvalidUser(self):
        invalidUserId = 3
        formData = {'user': invalidUserId}
        form = ShareCategoryForm(fromUser=self.user, category=self.category, data=formData)
        self.assertFalse(form.is_valid())
        self.assertTrue('user' in form.errors)

    # Tests the form with a user who is not a follower of the user, checks that the form is not valid and has an error for the user field.
    def testFormWithNonFollowerUser(self):
        nonFollowerUser = self.secondUser
        formData = {'user': nonFollowerUser.id}
        form = ShareCategoryForm(fromUser=self.user, category=self.category, data=formData)
        self.assertFalse(form.is_valid())
        self.assertTrue('user' in form.errors)

    # Tests the form with empty data, checks that the form is not valid and has an error for the user field
    def testFormWithEmptyData(self):
        form = ShareCategoryForm(fromUser=self.user, category=self.category, data={})
        self.assertFalse(form.is_valid())
        self.assertTrue('user' in form.errors)