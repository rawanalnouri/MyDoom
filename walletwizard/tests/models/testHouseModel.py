''' Tests for the House model'''

from walletwizard.models import House
from django.test import TestCase
from datetime import date
from django.core.exceptions import ValidationError

class HouseModelTestCase(TestCase):
    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):

        self.house = House.objects.get(id = 1)
    

    def testHouseIsValid(self):
        try:
            self.house.full_clean()
        except:
            self.fail('house must be valid')

    def testNoBlankPoints(self):
        self.house.points = None
        with self.assertRaises(ValidationError):
            self.house.full_clean()

    def testNoBlankName(self):
        self.house.name = None
        with self.assertRaises(ValidationError):
            self.house.full_clean()

    def testNoBlankMemberCount(self):
        self.house.memberCount = None
        with self.assertRaises(ValidationError):
            self.house.full_clean()

    def testNameWithinLengthLimit(self):
        self.house.name = "TCI5h49Wc6OLthsThldTZ3VKXxt3EhlEdcZgZJLYmnH4MOciYXqR41433LrOdBL5JU0te7RPRzNgyTxN3eBDBnl4osIWDLRHwmva0FBWZQYPGWDRdrN78mXYPwjBlz4HxKL9u59bvKOcGQ6sGDIedqY0GPprjoa1Yk9FiMbbhWXuRff0r4dftrwECyM7uCtyeNFxrD5BXEROrANuajTkgKIQI8IcpiezguQaxl0q8eXOFTb2Ix5M0YMhTzBhHa2s0YXI"
        with self.assertRaises(ValidationError):
            self.house.full_clean()
