'''Unit tests for the House model.'''
from walletwizard.models import House
from django.test import TestCase
from django.core.exceptions import ValidationError

class HouseModelTestCase(TestCase):
    '''Unit tests for the House model.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.house = House.objects.get(id=1)
        self.secondHouse = House.objects.get(id=2)

    def testPointsCannotBeNone(self):
        self.house.points = None
        with self.assertRaises(ValidationError):
            self.house.full_clean()

    def testNameCannotBeBlank(self):
        self.house.name = ''
        self._assertHouseIsInvalid
    
    def testNameMustBeUnique(self):
        self.house.name = self.secondHouse.name
        self._assertHouseIsInvalid()
    
    def testNameMustBeAtMostFiftyCharactersLong(self):
        self.house.name = 'x' * 51
        self._assertHouseIsInvalid()
    
    def testNameCanBeLessThanFiftyCharactersLong(self):
        self.house.name = 'x' * 25
        self._assertHouseIsValid()
    
    def testNameCanBeFiftyCharactersLong(self):
        self.house.name = 'x' * 50
        self._assertHouseIsValid()

    def testNameCannotBeNone(self):
        self.house.name = None
        self._assertHouseIsInvalid()

    def testMemberCountCannotBeNone(self):
        self.house.memberCount = None
        self._assertHouseIsInvalid()

    def testMemberCountCannotBeLessThanZero(self):
        self.house.memberCount = -1
        self._assertHouseIsInvalid()

    def testMemberCountCannotBeEqualToZero(self):
        self.house.memberCount = 0
        self._assertHouseIsValid()

    def _assertHouseIsValid(self):
        try:
            self.house.full_clean()
        except:
            self.fail('Test house should be valid')
    
    def _assertHouseIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.house.full_clean()
