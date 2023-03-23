'''Unit tests for the Expenditure model.'''
from walletwizard.models import Expenditure
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal

class ExpenditureModelTestCase(TestCase):
    '''Unit tests for the Expenditure model.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.expenditure = Expenditure.objects.get(id=1)


    def testTitleCannotBeNone(self):
        self.expenditure.title = None
        self._assertExpenditureIsInvalid()

    def testTitleCannotBeBlank(self):
        self.expenditure.title = ''
        self._assertExpenditureIsInvalid()

    def testTitleCannotBeMoreThan50CharactersLong(self):
        self.expenditure.title = 'x' * 51
        self._assertExpenditureIsInvalid()

    def testTitleCanBe50CharactersLong(self):
        self.expenditure.title = 'x' * 50
        self._assertExpenditureIsValid()
    

    def testDescriptionCanBeNone(self):
        self.expenditure.description = None
        self._assertExpenditureIsValid()

    def testDescriptionCanBeBlank(self):
        self.expenditure.description = ''
        self._assertExpenditureIsValid()

    def testDescriptionCannotBeMoreThan250CharactersLong(self):
        self.expenditure.description = 'x' * 251
        self._assertExpenditureIsInvalid()

    def testDescriptionCanBe50CharactersLong(self):
        self.expenditure.description = 'x' * 250
        self._assertExpenditureIsValid()


    def testDateCannotBeNone(self):
        self.expenditure.date = None
        self._assertExpenditureIsInvalid()

    def testDateCannotBeBlank(self):
        self.expenditure.date = ''
        self._assertExpenditureIsInvalid()

    def testDateCanBeInputAsString(self):
        self.expenditure.date = '2022-03-23'
        self._assertExpenditureIsValid()
    
    def testDateStringMustBeValid(self):
        self.expenditure.date = 'invalidDate'
        self._assertExpenditureIsInvalid()


    def testAmountCannotBeNone(self):
        self.expenditure.amount = None
        self._assertExpenditureIsInvalid()

    def testAmountCannotBeBlank(self):
        self.expenditure.amount = ''
        self._assertExpenditureIsInvalid()

    def testAmountHasMaximumTwoDecimalPlaces(self):
        self.expenditure.amount = 1234.1234
        self._assertExpenditureIsInvalid()

    def testAmountCanHaveNoDecimalPlaces(self):
        self.expenditure.amount = 1234
        self._assertExpenditureIsValid()

    def testAmountMustHaveMaximum10Digits(self):
        self.expenditure.amount = int('1'+'0'*9)
        self._assertExpenditureIsInvalid()

    def testAmountCannotHaveOneDecimalPlace(self):
        self.expenditure.amount = 1234.1
        self._assertExpenditureIsInvalid()

    def testAmountMustNotBeLessThanZero(self):
        self.expenditure.amount = -0.01
        self._assertExpenditureIsInvalid()
    
    def testAmountCannotBeEqualToZero(self):
        self.expenditure.amount = 0
        self._assertExpenditureIsInvalid()
    
    def testAmountMinimumValueCannotBeLessThanNoughtPointNoughtOne(self):
        self.expenditure.amount = Decimal('0.00').normalize()
        self._assertExpenditureIsInvalid()

    def testAmountMinimumValueMustBeGreaterThanNoughtPointNoughtOne(self):
        self.expenditure.amount =  Decimal('0.02').normalize()
        self._assertExpenditureIsValid()


    def testReceiptCanBeNone(self):
        self.expenditure.receipt = None
        self._assertExpenditureIsValid()

    def testReceiptCanBeBlank(self):
        self.expenditure.receipt = ''
        self._assertExpenditureIsValid()


    def testExpenditureToStringIsEqualToTitle(self):
        self.assertEqual(self.expenditure.title, str(self.expenditure))


    def _assertExpenditureIsValid(self):
        try:
            self.expenditure.full_clean()
        except:
            self.fail('Test expenditure should be valid')

    def _assertExpenditureIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.expenditure.full_clean() 