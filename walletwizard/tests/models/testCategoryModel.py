''' Tests for the Category model.'''
from walletwizard.models import Category, SpendingLimit, Expenditure, User
from django.test import TestCase
from django.core.exceptions import ValidationError

class CategoryModelTestCase(TestCase):
    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user1 = User.objects.get(id = 1)

        firstName2 = 'Jane'
        lastName2 = 'Smith'
        email2 = 'testEmail2@example.org'
        username2 = 'janesmith'
        password2 = "Password123"
        self.user2 = User.objects.create(
            username = username2,
            firstName = firstName2,
            lastName = lastName2,
            email = email2,
            password = password2
        )

        self.spendingLimit = SpendingLimit.objects.get(id = 1)
        self.expenditure = Expenditure.objects.get(id = 1)
        self.category = Category.objects.get(id = 1)

        self.category.users.add(self.user1)
        self.category.users.add(self.user2)
        self.category.spendingLimit = self.spendingLimit
        self.category.expenditures.add(self.expenditure)

    def testCategoryIsValid(self):
        try:
            self.category.full_clean()
        except:
            self.fail('category must be valid')

    def testNoBlankName(self):
        self.category.name = ''
        with self.assertRaises(ValidationError):
            self.category.full_clean()

    def testNoBlankSpendingLimit(self):
        self.category.spendingLimit = None
        with self.assertRaises(ValidationError):
            self.category.full_clean()

    def testNameWithinLengthLimit(self):
        self.category.name = 'x' * 81
        with self.assertRaises(ValidationError):
            self.category.full_clean()

    def testCategoryProgressWithZeroSpendingLimit(self):
        self.category.spendingLimit.amount = 0
        self.assertEqual(0, self.category.progressAsPercentage())

   










































































































   