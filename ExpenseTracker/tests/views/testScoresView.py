# Tests for the scores view

from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import Points, House, User

class ScoresViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
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

    # Test that the 'scores' page can be accessed
    def testGetScoresPage(self):
        response = self.client.get(reverse('scores'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scores.html')   

    # Test that the houses are displayed in the correct order on the 'scores' page
    def testHousesOrder(self):    
        response = self.client.get(reverse('scores'))
        houses = response.context['houses']
        self.assertEqual(houses[0], self.house2)
        self.assertEqual(houses[1], self.house1)

    # Test that the users are displayed in the correct order on the 'scores' page
    def testUserOrder(self):    
        response = self.client.get(reverse('scores'))
        users = response.context['points']
        self.assertEqual(users[0], self.points2)
        self.assertEqual(users[1], self.points1)

    # Test that the user is redirected to the login page if they are not logged in
    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('scores')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')