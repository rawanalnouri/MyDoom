'''Unit tests for the Points model.'''
from walletwizard.models import User, Points
from django.test import TestCase
from django.core.exceptions import ValidationError

class PointsModelTestCase(TestCase):
    '''Unit tests for the Points model.'''

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.points = Points.objects.get(id=1)

    def testUserCannotBeNone(self):
        self.points.user = None
        self._assertPointsIsInvalid()
    
    def testUserWithValidUser(self):
        self.points.user = self.user
        self._assertPointsIsValid()

    def testCountCannotBeNone(self):
        self.points.count = None
        self._assertPointsIsInvalid()

    def testCountCannotBeLessThanZero(self):
        self.points.count = -1
        self._assertPointsIsInvalid()

    def testCountCanBeEqualToZero(self):
        self.points.count = 0
        self._assertPointsIsValid()

    def testPointsUserInstanceIsTheSameAsUserModelInstance(self):
        userPoints = Points.objects.get(user=self.user)
        self.assertEqual(self.user.id, userPoints.user.id)

    def _assertPointsIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.points.full_clean()
    
    def _assertPointsIsValid(self):
        try:
            self.points.full_clean()
        except:
            self.fail('Test points should be valid')