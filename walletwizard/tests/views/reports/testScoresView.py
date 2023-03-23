"""Tests for the scores view."""
from django.test import TestCase
from django.urls import reverse
from walletwizard.models import Points, House, User
from walletwizard.tests.testHelpers import reverse_with_next

class ScoresViewTest(TestCase):
    """Tests for the scores view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.url = reverse('scores')
        self.house1 = House.objects.get(id=1)
        self.house2 = House.objects.get(id=2)
        self.user1 = User.objects.get(id=1)
        self.client.force_login(self.user1)
        self.user2 = User.objects.create(
            firstName = "Lucy",
            lastName = "Doe",
            username = "lcu123",
            email = "lucy@email.com",
            house = self.house2
        )
        self.points1 = Points.objects.get(id=1)
        self.points2 = Points.objects.create(user = self.user2, count = 75)

    def testGetScoresPage(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scores.html')   

    def testHousesOrder(self):    
        response = self.client.get(self.url)
        houses = response.context['houses']
        self.assertEqual(houses[0], self.house2)
        self.assertEqual(houses[1], self.house1)

    def testUserOrder(self):    
        response = self.client.get(self.url)
        users = response.context['userPoints']
        self.assertEqual(users[0], self.points2)
        self.assertEqual(users[1], self.points1)

    def testScoresViewRedirectsToLoginIfNotLoggedIn(self):
        self.client.logout()
        redirectUrl = reverse_with_next('logIn', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed('logIn.html')