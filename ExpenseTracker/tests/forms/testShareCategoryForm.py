from django.test import TestCase
from ExpenseTracker.models import User, Category
from ExpenseTracker.forms import ShareCategoryForm


class ShareCategoryFormTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

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

    def testFormWithValidData(self):
        validUser = self.secondUser
        self.user.followers.add(validUser)
        formData = {'user': validUser.id}
        form = ShareCategoryForm(user=self.user, category=self.category, data=formData)
        self.assertTrue(form.is_valid(), form.errors)
        category = form.save()
        self.assertTrue(validUser in category.users.all())
        self.assertTrue(self.category in validUser.categories.all())

    def testFormWithInvalidUser(self):
        invalidUserId = 3
        formData = {'user': invalidUserId}
        form = ShareCategoryForm(user=self.user, category=self.category, data=formData)
        self.assertFalse(form.is_valid())
        self.assertTrue('user' in form.errors)

    def testFormWithNonFollowerUser(self):
        nonFollowerUser = self.secondUser
        formData = {'user': nonFollowerUser.id}
        form = ShareCategoryForm(user=self.user, category=self.category, data=formData)
        self.assertFalse(form.is_valid())
        self.assertTrue('user' in form.errors)

    def testFormWithEmptyData(self):
        form = ShareCategoryForm(user=self.user, category=self.category, data={})
        self.assertFalse(form.is_valid())
        self.assertTrue('user' in form.errors)
