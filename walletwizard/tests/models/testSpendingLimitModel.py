'''Tests for the SpendingLimit model.'''
from walletwizard.models import SpendingLimit
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal

class SpendingLimitModelTestCase(TestCase):
    '''Tests for the SpendingLimit model.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.spendingLimit = SpendingLimit.objects.get(id=1)

    def testTimePeriodCannotBeNone(self):
        self.spendingLimit.timePeriod = None
        self._assertSpendingLimitIsInvalid()

    def testTimePeriodCannotBlank(self):
        self.spendingLimit.timePeriod = ''
        self._assertSpendingLimitIsInvalid()

    def testInvalidTimePeriodChoice(self):
        self.spendingLimit.timePeriod = 'invalidChoice'
        self._assertSpendingLimitIsInvalid()

    def testTimePeriodCanBeFromSpendingLimitTimePeriodChoices(self):
        for choice in SpendingLimit.TIME_CHOICES:
            self.spendingLimit.timePeriod = choice[0]
            self._assertSpendingLimitIsValid()

    def testTimePeriodCanBeLessThanTwentyCharacters(self):
        self.spendingLimit.timePeriod = 'weekly'
        self._assertSpendingLimitIsValid()

    def testAmountHasMaximumTwoDecimalPlaces(self):
        self.spendingLimit.amount = 1234.1234
        self._assertSpendingLimitIsInvalid()

    def testAmountCanHaveNoDecimalPlaces(self):
        self.spendingLimit.amount = 1234
        self._assertSpendingLimitIsValid()

    def testAmountCannotHaveOneDecimalPlace(self):
        self.spendingLimit.amount = 1234.1
        self._assertSpendingLimitIsInvalid()

    def testAmountMustNotBeLessThanZero(self):
        self.spendingLimit.amount = -0.01
        self._assertSpendingLimitIsInvalid()
    
    def testAmountCannotBeEqualToZero(self):
        self.spendingLimit.amount = 0
        self._assertSpendingLimitIsInvalid()
    
    def testAmountMinimumValueCannotBeLessThanNoughtPointNoughtOne(self):
        self.spendingLimit.amount = Decimal('0.00').normalize()
        self._assertSpendingLimitIsInvalid()

    def testAmountMinimumValueMustBeGreaterThanNoughtPointNoughtOne(self):
        self.spendingLimit.amount =  Decimal('0.02').normalize()
        self._assertSpendingLimitIsValid()

    def testCorrectAmountReturned(self):
        self.assertEqual(self.spendingLimit.amount, self.spendingLimit.getNumber())

    def _assertSpendingLimitIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.spendingLimit.full_clean()
    
    def _assertSpendingLimitIsValid(self):
        try:
            self.spendingLimit.full_clean()
        except:
            self.fail('Test spending limit should be valid')