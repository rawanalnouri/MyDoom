''' Tests for the SpendingLimit model'''

from ExpenseTracker.models import SpendingLimit
from django.test import TestCase
from django.core.exceptions import ValidationError

class SpendingLimitModelTestCase(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.spendingLimit = SpendingLimit.objects.get(id=1)


    def testSpendingLimitIsValid(self):
        try:
            self.spendingLimit.full_clean()
        except:
            self.fail('Spending Limit must be valid')

    def testNoBlankTimePeriod(self):
        self.spendingLimit.timePeriod = None
        with self.assertRaises(ValidationError):
            self.spendingLimit.full_clean()

    def testNoBlankAmount(self):
        self.spendingLimit.amount = None
        with self.assertRaises(ValidationError):
            self.spendingLimit.full_clean()

    def testTimePeriodWithinLengthLimit(self):
        self.spendingLimit.timePeriod = "TCI5h49Wc6OLthsThldTZ3VKXxt3EhlEdcZgZJLYmnH4MOciYXqR41433LrOdBL5JU0te7RPRzNgyTxN3eBDBnl4osIWDLRHwmva0FBWZQYPGWDRdrN78mXYPwjBlz4HxKL9u59bvKOcGQ6sGDIedqY0GPprjoa1Yk9FiMbbhWXuRff0r4dftrwECyM7uCtyeNFxrD5BXEROrANuajTkgKIQI8IcpiezguQaxl0q8eXOFTb2Ix5M0YMhTzBhHa2s0YXI"
        with self.assertRaises(ValidationError):
            self.spendingLimit.full_clean()

    def testTimePeriodIsValid(self):
        self.spendingLimit.timePeriod = "test"
        with self.assertRaises(ValidationError):
            self.spendingLimit.full_clean()

    def testAmountWithinLengthLimit(self):
        self.spendingLimit.amount = 123456789.12
        with self.assertRaises(ValidationError):
            self.spendingLimit.full_clean()

    def testAmountWithinDecimalLimit(self):
        self.spendingLimit.amount = 1234.1234
        with self.assertRaises(ValidationError):
            self.spendingLimit.full_clean()

    def testAmountNotNegative(self):
        self.spendingLimit.amount = -0.01
        with self.assertRaises(ValidationError):
            self.spendingLimit.full_clean()

    def testCorrectAmountReturned(self):
        self.assertEqual(self.spendingLimit.amount, self.spendingLimit.getNumber())