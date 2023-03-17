from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import Points, House, User

# ests the functionality of the scores page in the ExpenseTracker application,
# ensuring that it is displaying the correct data and redirecting unauthenticated users to the login page.

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
        self.points2 = Points.objects.create(user = self.user2, pointsNum = 75)

#  test to see if scores page is accessible and if the correct template is used.
    def testGetScoresPage(self):
        response = self.client.get(reverse('scores'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scores.html')   

    def testHousesOrder(self):    
        response = self.client.get(reverse('scores'))
        houses = response.context['houses']
        self.assertEqual(houses[0], self.house2)
        self.assertEqual(houses[1], self.house1)

    def testUserOrder(self):    
        response = self.client.get(reverse('scores'))
        users = response.context['users']
        self.assertEqual(users[0], self.points2)
        self.assertEqual(users[1], self.points1)

    def testRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = reverse('scores')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')
        

          




