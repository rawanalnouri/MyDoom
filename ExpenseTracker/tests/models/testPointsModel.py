from ExpenseTracker.models import User, Points
from django.test import TestCase
from django.core.exceptions import ValidationError


class PointsModelTestCase(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.points = Points.objects.create(
            user = self.user,
            pointsNum = 10
        )

    def testNoBlankTitle(self):
        self.points.user = None
        with self.assertRaises(ValidationError):
            self.points.full_clean()

    def testNoBlankPoints(self):
        self.points.pointsNum = None
        with self.assertRaises(ValidationError):
            self.points.full_clean()

    def testUserExists(self):
        self.user.save()
        user = User.objects.get(email = self.points.user.email)
        self.assertEqual(user, self.points.user)
