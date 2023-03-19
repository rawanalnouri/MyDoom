# Tests for the create expenditure view

from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, Points, Notification
from ExpenseTracker.forms import ExpenditureForm
import datetime
from ExpenseTracker.tests.helpers import *

class CreateExpenditureViewTest(TestCase):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.client.force_login(self.user)
        self.category = Category.objects.get(id=1)
        self.category.users.add(self.user)
        self.url = reverse('createExpenditure', kwargs={'categoryId': self.category.id})

        self.data = {
            'title': 'testexpenditure2', 
            'date': datetime.date.today(), 
            'amount': 10,
            'otherCategory': -1,
        }

    # This test checks whether the correct template and form are being used when creating a new expenditure.
    def test_get_create_expenditure_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], ExpenditureForm)
    
    # This test checks whether a new expenditure is created successfully when the form data is valid.
    def testCreateExpenditureViewWhenFormIsValid(self):
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, '/category/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expenditure.objects.count(), 2)
        self.assertTrue(Expenditure.objects.filter(title='testexpenditure2').exists())
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Expenditure created successfully."
        self.assertEqual(str(messages[0]), expectedMessage)
    
    # This test checks whether a new expenditure is not created when the form data is invalid.
    def testCreateExpenditureViewWhenFormIsInvalid(self):
        self.data['title'] = ''
        self.data['date'] = ''
        self.data['amount'] = -1
        response = self.client.post(self.url, self.data)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        expectedMessage = "Failed to create expenditure."
        self.assertEqual(str(messages[0]), expectedMessage)
        self.assertEqual(Expenditure.objects.count(), 1)
        self.assertEqual(Expenditure.objects.first().title, 'testexpenditure')

    # This test checks whether a user is redirected to the login page when they try to edit a category while not logged in.
    def testEditCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = self.url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')

    # This test checks whether a user gains five points when they create an expenditure that stays within the category's spending limit.
    def testUserGainsFivePointsForStayingWithinLimit(self):
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have increased
        self.assertEqual(userPointsAfter, userPointsBefore+5)
        # Check if user received points notification
        notifications = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:2]
        titles=getNotificationTitles(notifications)
        messages=getNotificationMessages(notifications)
        self.assertIn("House points gained!", titles)
        self.assertIn(str(self.user.house.name) + " has gained 5 points", messages)
        self.assertIn("Points Won!", titles)
        self.assertIn("5 points for staying within target for " + self.category.name, messages)
        
    # This test checks if a user recieves a notification when they near the spending limit.
    def testUserRecievesNotificationForNearingSpendingLimit(self):
        self.data['amount'] = 17
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have increased, as still within limit.
        self.assertEqual(userPointsAfter, userPointsBefore+5)
        notifications = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:3]
        titles=getNotificationTitles(notifications)
        messages=getNotificationMessages(notifications)
        # Check if user receives notification for nearing limit.
        self.assertIn("You are nearing your spending limit for " + self.category.name, messages)
        self.assertIn("Watch out!", titles )
        # Check if user gets house points notifications.
        self.assertIn("House points gained!", titles)
        self.assertIn(str(self.user.house.name) + " has gained 5 points", messages)
        # Check if user received points notification.
        self.assertIn("Points Won!", titles)
        self.assertIn("5 points for staying within target for " + self.category.name, messages)
     
    #  This test checks whether a user loses points when they reate an expenditure that is at the spending limit.
    def testUserDoesnntLosePointsIfAtLimit(self):
        self.data['amount'] = 20
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have increased
        self.assertEqual(userPointsAfter, userPointsBefore+5)

    # This test checks whether a user loses three points when they create an expenditure that is 10% over the spending limit.
    def testUserLosesThreePointsIfTenPercentOverLimit(self):
        self.data['amount'] = 22
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have decreased as 10% over limit.
        self.assertEqual(userPointsAfter, userPointsBefore-3)
       # Check if user receives notification for losing points.
        notifications = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:2]
        titles=getNotificationTitles(notifications)
        messages=getNotificationMessages(notifications)
        self.assertIn("House points lost!", titles)
        self.assertIn(str(self.user.house.name) + " has lost 3 points", messages)
        self.assertIn("Points Lost!", titles)
        self.assertIn("3 points lost for going over target", messages) 

    #  This test checks whether a user loses five points when they create an expenditure that is between 10% and 30% over the spending limit.
    def testUserLosesFivePointsIfTenToThirtyPercentOver(self):
        self.data['amount'] = 26
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have decreased as 30% over limit
        self.assertEqual(userPointsAfter, userPointsBefore-5)
       # Check if user receives notification for losing points
        notifications = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:2]
        titles=getNotificationTitles(notifications)
        messages=getNotificationMessages(notifications)
        self.assertIn("House points lost!", titles)
        self.assertIn(str(self.user.house.name) + " has lost 5 points", messages)
        self.assertIn("Points Lost!", titles)
        self.assertIn("5 points lost for going over target", messages) 

    # This test case checks if the user loses 10 points if they spend between 30% to 50% over their target expenditure limit. 
    def testUserLosesTenPointsIfThirtyToFiftyPercentOver(self):
        self.data['amount'] = 30
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have decreased as 50% over limit
        self.assertEqual(userPointsAfter, userPointsBefore-10)
       # Check if user receives notification for losing points
        notifications = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:2]
        titles=getNotificationTitles(notifications)
        messages=getNotificationMessages(notifications)
        self.assertIn("House points lost!", titles)
        self.assertIn(str(self.user.house.name) + " has lost 10 points", messages)
        self.assertIn("Points Lost!", titles)
        self.assertIn("10 points lost for going over target", messages) 

    # This test case checks if the user loses 15 points if they spend between 50% to 70% over their target expenditure limit. 
    def testUserLosesFifteenPointsIfFiftyToSeventyPercentOver(self):
        self.data['amount'] = 34
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have decreased as 50% over limit
        self.assertEqual(userPointsAfter, userPointsBefore-15)
       # Check if user receives notification for losing points
        notifications = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:2]
        titles=getNotificationTitles(notifications)
        messages=getNotificationMessages(notifications)
        self.assertIn("House points lost!", titles)
        self.assertIn(str(self.user.house.name) + " has lost 15 points", messages)
        self.assertIn("Points Lost!", titles)
        self.assertIn("15 points lost for going over target", messages) 

    #  This test case checks if the user loses 20 points if they spend between 70% to 100% over their target expenditure limit.
    def testUserLosesTwentyPointsIfSeventyToHundredPercentOver(self):
        self.data['amount'] = 40
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have decreased as 50% over limit.
        self.assertEqual(userPointsAfter, userPointsBefore-20)
       # Check if user receives notification for losing points.
        notifications = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:2]
        titles=getNotificationTitles(notifications)
        messages=getNotificationMessages(notifications)
        self.assertIn("House points lost!", titles)
        self.assertIn(str(self.user.house.name) + " has lost 20 points", messages)
        self.assertIn("Points Lost!", titles)
        self.assertIn("20 points lost for going over target", messages) 

    #  This test case checks if the user loses 25 points if they spend over 100% of their target expenditure limit.
    def testUserLosesTwentyFivePointsIfOverHundredPercent(self):
        self.data['amount'] = 41
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have decreased as 50% over limit.
        self.assertEqual(userPointsAfter, userPointsBefore-25)
       # Check if user receives notification for losing points.
        notifications = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:2]
        titles=getNotificationTitles(notifications)
        messages=getNotificationMessages(notifications)
        self.assertIn("House points lost!", titles)
        self.assertIn(str(self.user.house.name) + " has lost 25 points", messages)
        self.assertIn("Points Lost!", titles)
        self.assertIn("25 points lost for going over target", messages) 

    # This test case checks if the user loses the correct number of points if they are already over 
    # their target expenditure limit before making a new expense entry.
    def testUserLosesCorrectPointsIfAlreadyOverLimit(self):
        previousExpenditure = Expenditure.objects.get(id=1)
        previousExpenditure.amount = 45
        previousExpenditure.date = datetime.date.today()
        previousExpenditure.save()
        self.category.expenditures.add(previousExpenditure)

        # Should only lose 3 points.
        self.data['amount'] = 1
        userPointsBefore = Points.objects.get(user=self.user).count
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        self.assertEqual(userPointsAfter, userPointsBefore-3)

    #  This test case checks if the user's points cannot go below zero, even if 
    # they spend more than their target expenditure limit and are already low on points.
    def testUserPointsCantBeNegative(self):
        # Set user points to low value
        userPoints = Points.objects.get(id=1)
        userPoints.count = 3
        userPoints.save()
        # User should lose 25 points, but points are low - so points should be 0
        self.data['amount'] = 45
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).count
        self.assertEqual(userPointsAfter, 0)