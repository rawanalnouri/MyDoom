from django.test import TestCase
from django.urls import reverse
from ExpenseTracker.models import User, Category, Expenditure, Points, Notification
from ExpenseTracker.forms import ExpenditureForm
import datetime

#tests for the create expenditure view

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
            'amount': 10
        }

    # This test checks whether the correct template and form are being used 
    # when creating a new expenditure.
    def test_get_create_expenditure_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/bootstrapForm.html')
        self.assertIsInstance(response.context['form'], ExpenditureForm)
    
    # This test checks whether a new expenditure is created successfully
    # when the form data is valid.
    # 
    #  It also checks whether a success message is displayed and 
    # the user is redirected to the correct page.
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
    # 
    #  It also checks whether an error message is displayed.
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

    # This test checks whether a user is redirected to the login 
    # page when they try to edit a category while not logged in.
    def testEditCategoryViewRedirectIfNotLoggedIn(self):
        self.client.logout()
        url = self.url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('logIn'))
        self.assertTemplateUsed('logIn.html')

    # This test checks whether a user gains five points when they create an expenditure that
    # stays within the category's spending limit.
    # 
    #  It also checks whether the user receives a notification about the points they earned.
    def testUserGainsFivePointsForStayingWithinLimit(self):
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        # Check if user points have increased
        self.assertEqual(userPointsAfter, userPointsBefore+5)
        # Check if user received points notification
        notification = Notification.objects.filter(toUser=self.user).latest('createdAt')
        self.assertEqual(notification.title, "Points Won!")
        self.assertEqual(notification.message, "5 points for staying within target for " + self.category.name)

    # This test checks whether a user receives a notification when they are 
    # nearing their spending limit.
    # 
    #  It also checks whether the user still gains points when they create an expenditure 
    # that is just under the limit.
    def testUserRecievesNotificationForNearingSpendingLimit(self):
        self.data['amount'] = 17
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        # Check if user points have increased, as still within limit
        self.assertEqual(userPointsAfter, userPointsBefore+5)
        notificationsReceived = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:2]
       # Check if user received points notification
        notification = Notification.objects.filter(toUser=self.user).latest('createdAt')
        self.assertEqual(notificationsReceived[0].title, "Points Won!")
        self.assertEqual(notificationsReceived[0].message, "5 points for staying within target for " + self.category.name)
        # Check if user receives notification for nearing limit
        self.assertEqual(notificationsReceived[1].title, "Watch out!")
        self.assertEqual(notificationsReceived[1].message, "You are nearing your spending limit for " + self.category.name)
     
    #  This test checks whether a user loses points when they 
    # create an expenditure that is at the spending limit.
    def testUserDoesnntLosePointsIfAtLimit(self):
        self.data['amount'] = 20
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        # Check if user points have increased
        self.assertEqual(userPointsAfter, userPointsBefore+5)

    # This test checks whether a user loses three points when they create an expenditure
    #  that is 10% over the spending limit.
    # 
    #  It also checks whether the user receives a notification
    #  about the points they lost.
    def testUserLosesThreePointsIfTenPercentOverLimit(self):
        self.data['amount'] = 22
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        # Check if user points have decreased as 10% over limit
        self.assertEqual(userPointsAfter, userPointsBefore-3)
       # Check if user receives notification for losing points
        notification = Notification.objects.filter(toUser=self.user).latest('createdAt')
        self.assertEqual(notification.title, "Points Lost!")
        self.assertEqual(notification.message, "3 points lost for going over target")

    #  This test checks whether a user loses five points when they 
    # create an expenditure that is between 10% and 30% over the
    # spending limit.
    # 
    #  It also checks whether the user receives a notification 
    # about the points they lost.
    def testUserLosesFivePointsIfTenToThirtyPercentOver(self):
        self.data['amount'] = 26
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        # Check if user points have decreased as 30% over limit
        self.assertEqual(userPointsAfter, userPointsBefore-5)
       # Check if user receives notification for losing points
        notification = Notification.objects.filter(toUser=self.user).latest('createdAt')
        self.assertEqual(notification.title, "Points Lost!")
        self.assertEqual(notification.message, "5 points lost for going over target")  
    
    # This test checks whether a user loses ten points when they create 
    # an expenditure that is between 30% and 50% over the spending limit.
    # 
    #  It also checks whether the user receives a notification 
    # about the points they lost.
    def testUserLosesTenPointsIfThirtyToFiftyPercentOver(self):
        self.data['amount'] = 30
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        # Check if user points have decreased as 50% over limit
        self.assertEqual(userPointsAfter, userPointsBefore-10)
       # Check if user receives notification for losing points
        notification = Notification.objects.filter(toUser=self.user).latest('createdAt')
        self.assertEqual(notification.title, "Points Lost!")
        self.assertEqual(notification.message, "10 points lost for going over target") 

    # This test case checks if the user loses 15 points if they spend between 
    # 50% to 70% over their target expenditure limit. 
    # 
    # It also verifies if a notification is sent to the user informing 
    # them about the points lost.
    def testUserLosesFifteenPointsIfFiftyToSeventyPercentOver(self):
        self.data['amount'] = 34
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        # Check if user points have decreased as 50% over limit
        self.assertEqual(userPointsAfter, userPointsBefore-15)
       # Check if user receives notification for losing points
        notification = Notification.objects.filter(toUser=self.user).latest('createdAt')
        self.assertEqual(notification.title, "Points Lost!")
        self.assertEqual(notification.message, "15 points lost for going over target") 

    #  This test case checks if the user loses 20 points if they spend between 
    # 70% to 100% over their target expenditure limit.
    # 
    #  It also verifies if a notification is sent to the user informing 
    # them about the points lost.
    def testUserLosesTwentyPointsIfSeventyToHundredPercentOver(self):
        self.data['amount'] = 40
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        # Check if user points have decreased as 50% over limit
        self.assertEqual(userPointsAfter, userPointsBefore-20)
       # Check if user receives notification for losing points
        notification = Notification.objects.filter(toUser=self.user).latest('createdAt')
        self.assertEqual(notification.title, "Points Lost!")
        self.assertEqual(notification.message, "20 points lost for going over target") 

    #  This test case checks if the user loses 25 points if they spend over 
    # 100% of their target expenditure limit.
    # 
    #  It also verifies if a notification is sent to the user 
    # informing them about the points lost.
    def testUserLosesTwentyFivePointsIfOverHundredPercent(self):
        self.data['amount'] = 41
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        # Check if user points have decreased as 50% over limit
        self.assertEqual(userPointsAfter, userPointsBefore-25)
       # Check if user receives notification for losing points
        notification = Notification.objects.filter(toUser=self.user).latest('createdAt')
        self.assertEqual(notification.title, "Points Lost!")
        self.assertEqual(notification.message, "25 points lost for going over target") 

    # This test case checks if the user loses the correct number 
    # of points if they are already over their target expenditure
    #  limit before making a new expense entry.
    def testUserLosesCorrectPointsIfAlreadyOverLimit(self):
        previousExpenditure = Expenditure.objects.get(id=1)
        previousExpenditure.amount = 45
        previousExpenditure.date = datetime.date.today()
        previousExpenditure.save()
        self.category.expenditures.add(previousExpenditure)

        # Should only lose 3 points
        self.data['amount'] = 1
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        self.assertEqual(userPointsAfter, userPointsBefore-3)

    #  This test case checks if the user's points cannot go below zero,
    #  even if they spend more than their target expenditure limit and are already 
    # low on points.
    # 
    #  It verifies if the user's points are set to zero instead of negative values.
    def testUserPointsCantBeNegative(self):
        # Set user points to low value
        userPoints = Points.objects.get(id=1)
        userPoints.pointsNum = 3
        userPoints.save()
        # User should lose 25 points, but points are low - so points should be 0
        self.data['amount'] = 45
        self.client.post(self.url, self.data)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum
        self.assertEqual(userPointsAfter, 0)






