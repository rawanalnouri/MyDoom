from ExpenseTracker.models import Expenditure
from django.test import TestCase
from django.core.exceptions import ValidationError


class ExpenditureModelTestCase(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.expenditure = Expenditure.objects.get(id=1)

    def testExpenditureIsValid(self):
        try:
            self.expenditure.full_clean()
        except:
            self.fail('Expenditure must be valid')

    def testNoBlankTitle(self):
        self.expenditure.title = None
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean()

    def testNoBlankAmount(self):
        self.expenditure.amount = None
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean()

    def testNoBlankDate(self):
        self.expenditure.date = None
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean()

    def testTitleWithinLengthLimit(self):
        self.expenditure.title = "TCI5h49Wc6OLthsThldTZ3VKXxt3EhlEdcZgZJLYmnH4MOciYXqR41433LrOdBL5JU0te7RPRzNgyTxN3eBDBnl4osIWDLRHwmva0FBWZQYPGWDRdrN78mXYPwjBlz4HxKL9u59bvKOcGQ6sGDIedqY0GPprjoa1Yk9FiMbbhWXuRff0r4dftrwECyM7uCtyeNFxrD5BXEROrANuajTkgKIQI8IcpiezguQaxl0q8eXOFTb2Ix5M0YMhTzBhHa2s0YXI"
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean()

    def testAmountWithinLengthLimit(self):
        self.expenditure.amount = 123456789.12
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean()

    def testAmountWithinDecimalLimit(self):
        self.expenditure.amount = 1234.1234
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean()

    def testAmountNotNegative(self):
        self.expenditure.amount = -0.01
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean()

    def testCorrectStringReturned(self):
        self.assertEqual(self.expenditure.title, str(self.expenditure))

