''' Tests for the User model'''

from ExpenseTracker.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError

class UserModelTestCase(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):

        # For basic user model
        firstName = 'John'
        lastName = 'Doe'
        email = 'testEmail1@example.org'
        username = 'johndoe'
        password = "Password123"
        self.user = User.objects.create(
            username = username,
            firstName = firstName,
            lastName = lastName,
            email = email,
            password = password
        )

        # For extended users
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

    def testUserIsValid(self):
        try:
            self.user.full_clean()
        except:
            self.fail('user must be valid')

    def testNoBlankUsername(self):
        self.user.username = None
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testUsernameCanBe30CharactersLong(self):
        self.user.username = 'x' * 30
        self.user.full_clean()

    def testUsernameCannotBeOver30CharactersLong(self):
        self.user.username = 'x' * 31
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testUsernameMustBeUnique(self):
        self.user.username = self.user2.username
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testUsernameContainsOnlyAlphanumericals(self):
        self.user.username = 'john!doe'
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testUsernameContainAtLeast3Alphanumericals(self):
        self.user.username = 'jo'
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testUsernameCanContainNumbers(self):
        self.user.username = 'j0hndoe2'
        self.user.full_clean()

    def testNoBlankFirstName(self):
        self.user.firstName = None
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testNoBlankLastName(self):
        self.user.lastName = None
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testNoBlankEmail(self):
        self.user.email = None
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testFirstNameWithinLengthLimit(self):
        self.user.firstName = "TCI5h49Wc6OLthsThldTZ3VKXxt3EhlEdcZgZJLYmnH4MOciYXqR41433LrOdBL5JU0te7RPRzNgyTxN3eBDBnl4osIWDLRHwmva0FBWZQYPGWDRdrN78mXYPwjBlz4HxKL9u59bvKOcGQ6sGDIedqY0GPprjoa1Yk9FiMbbhWXuRff0r4dftrwECyM7uCtyeNFxrD5BXEROrANuajTkgKIQI8IcpiezguQaxl0q8eXOFTb2Ix5M0YMhTzBhHa2s0YXIa;lkdfj"
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testLastNameWithinLengthLimit(self):
        self.user.lastName = "TCI5h49Wc6OLthsThldTZ3VKXxt3EhlEdcZgZJLYmnH4MOciYXqR41433LrOdBL5JU0te7RPRzNgyTxN3eBDBnl4osIWDLRHwmva0FBWZQYPGWDRdrN78mXYPwjBlz4HxKL9u59bvKOcGQ6sGDIedqY0GPprjoa1Yk9FiMbbhWXuRff0r4dftrwECyM7uCtyeNFxrD5BXEROrANuajTkgKIQI8IcpiezguQaxl0q8eXOFTb2Ix5M0YMhTzBhHa2s0YXI"
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testNoBlankEmail(self):
        self.user.email = ''
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testEmailMustBeUnique(self):
        self.user.email = self.user2.email
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testMustContainAUsername(self):
        self.user.email = '@example.org'
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testMustContainAtSymbol(self):
        self.user.email = 'johndoe.example.org'
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testMustContainDomainName(self):
        self.user.email = 'johndoe@.org'
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testMustContainDomain(self):
        self.user.email = 'johndoe@example'
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def testOnlyOneAt(self):
        self.user.email = 'johndoe@@example.org'
        with self.assertRaises(ValidationError):
            self.user.full_clean()