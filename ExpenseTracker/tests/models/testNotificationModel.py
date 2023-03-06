from ExpenseTracker.models import Notification, User
from django.test import TestCase
from datetime import date
from django.core.exceptions import ValidationError


class NotificationModelTestCase(TestCase):
    def setUp(self):

        #For basic notification model
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

        self.notification = Notification.objects.create(
            toUser = self.user,
            title = "Test Title",
            message = "This is a notification message text for test purposes.",
            type = 'basic'
        )

        #For extended notifications
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

        self.notification2 = Notification.objects.create(
            toUser = self.user,
            title = "Test Title",
            message = "This is a notification message text for test purposes.",
            type = 'basic'
        )

    def testNotificationIsValid(self):
        try:
            self.notification.full_clean()
        except:
            self.fail('Notification must be valid')

    def testNoBlankUser(self):
        self.notification.toUser = None
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testNoBlankTitle(self):
        self.notification.title = None
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testNoBlankMessage(self):
        self.notification.message = None
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testNoBlankIsSeenField(self):
        self.notification.isSeen = None
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testNoBlankType(self):
        self.notification.type = None
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testTitleWithinLengthLimit(self):
        self.notification.title = "TCI5h49Wc6OLthsThldTZ3VKXxt3EhlEdcZgZJLYmnH4MOciYXqR41433LrOdBL5JU0te7RPRzNgyTxN3eBDBnl4osIWDLRHwmva0FBWZQYPGWDRdrN78mXYPwjBlz4HxKL9u59bvKOcGQ6sGDIedqY0GPprjoa1Yk9FiMbbhWXuRff0r4dftrwECyM7uCtyeNFxrD5BXEROrANuajTkgKIQI8IcpiezguQaxl0q8eXOFTb2Ix5M0YMhTzBhHa2s0YXI"
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testMessageWithinLengthLimit(self):
        self.notification.message = "TCI5h49Wc6OLthsThldTZ3VKXxt3EhlEdcZgZJLYmnH4MOciYXqR41433LrOdBL5JU0te7RPRzNgyTxN3eBDBnl4osIWDLRHwmva0FBWZQYPGWDRdrN78mXYPwjBlz4HxKL9u59bvKOcGQ6sGDIedqY0GPprjoa1Yk9FiMbbhWXuRff0r4dftrwECyM7uCtyeNFxrD5BXEROrANuajTkgKIQI8IcpiezguQaxl0q8eXOFTb2Ix5M0YMhTzBhHa2s0YXIa;lkdfj"
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testUserExists(self):
        self.user.save()
        user = User.objects.get(email = self.notification.toUser.email)
        self.assertEqual(user, self.notification.toUser)

    #def testCreatedDateIsNow
