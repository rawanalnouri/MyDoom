from ExpenseTracker.models import Notification, User
from django.test import TestCase
from datetime import date
from django.core.exceptions import ValidationError


class NotificationModelTestCase(TestCase):
    def setUp(self):
        firstName = 'John'
        lastName = 'Doe'
        email = f'{firstName}.{lastName}@example.org'
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
            user = self.user
            title = "Test Title"
            message = "This is a notification message text for test purposes."
        )

    def testNotificationIsValid(self):
        try:
            self.notification.full_clean()
        except:
            self.fail('Notification must be valid')

    def testNoBlankUser(self):
        self.notification.user = None
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

    def testNoBlankDate(self):
        self.notification.createdAt = None
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testTitleWithinLengthLimit(self):
        self.notification.title = "TCI5h49Wc6OLthsThldTZ3VKXxt3EhlEdcZgZJLYmnH4MOciYXqR41433LrOdBL5JU0te7RPRzNgyTxN3eBDBnl4osIWDLRHwmva0FBWZQYPGWDRdrN78mXYPwjBlz4HxKL9u59bvKOcGQ6sGDIedqY0GPprjoa1Yk9FiMbbhWXuRff0r4dftrwECyM7uCtyeNFxrD5BXEROrANuajTkgKIQI8IcpiezguQaxl0q8eXOFTb2Ix5M0YMhTzBhHa2s0YXI"
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testMessageWithinLengthLimit(self):
        self.notification.price = "TCI5h49Wc6OLthsThldTZ3VKXxt3EhlEdcZgZJLYmnH4MOciYXqR41433LrOdBL5JU0te7RPRzNgyTxN3eBDBnl4osIWDLRHwmva0FBWZQYPGWDRdrN78mXYPwjBlz4HxKL9u59bvKOcGQ6sGDIedqY0GPprjoa1Yk9FiMbbhWXuRff0r4dftrwECyM7uCtyeNFxrD5BXEROrANuajTkgKIQI8IcpiezguQaxl0q8eXOFTb2Ix5M0YMhTzBhHa2s0YXI"
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def testUserExists(self):
        self.user.save()
        user = User.objects.get(email = self.notification.user.email)
        self.assertEqual(user, self.notification.user)

    # def testCreatedDateIsNow
