from ExpenseTracker.models import User, Points, Notification
from ExpenseTracker.forms import LogInForm
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from ExpenseTracker.tests.helpers import LogInTester
from datetime import datetime, timedelta
from django.utils import timezone

#tests for the login view

class TestLoginView(TestCase, LogInTester):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.input = {
            'username': 'bob123',
            'password': 'Password123'
        }
        self.url = reverse('logIn')


    # This test checks if the URL for the log in page is correct.
    def testLogInUrl(self):
        self.assertEqual(self.url, '/logIn/')

    # This test checks if the log in page can be accessed successfully
    #  by a GET request. 
    # 
    # It also checks if the correct template is being used and if the 
    # login form is being passed to the context. Finally, it checks that 
    # there are no messages being passed to the context.
    def testGetLogIn(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logIn.html')
        loginForm = response.context['form']
        self.assertTrue(isinstance(loginForm, LogInForm))
        self.assertFalse(loginForm.is_bound) 
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages),0)

    # This test checks if a user who is already authenticated
    #  is redirected to the home page when they try to access the log in page.
    def testRedirectToHomeIfUserAuthenticated(self):
        # User should be taken to the home page if logged in
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        userHomePage = reverse('home')
        self.assertRedirects(response, userHomePage, status_code=302, target_status_code=200)

    # This test checks if an unsuccessful login attempt generates the correct
    #  error message and that the user is not logged in.
    def testUnsuccessfulLogin(self):
        self.input['password'] = ''
        response = self.client.post(self.url, self.input)
        self.assertFalse(self.isUserLoggedIn())
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        #Check for error message
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages),1)
        self.assertEqual(listOfMessages[0].level, messages.ERROR)

    # This test checks if a successful login attempt redirects the user to the home page and if
    # the correct template is being used. 
    # 
    # It also checks that there are no messages being passed to the context.   
    def testSuccessfulLogInAndRedirect(self):
        response = self.client.post(self.url, self.input, follow=True)
        self.assertTrue(self.isUserLoggedIn())
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        #No Error Messages recieved
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages), 0)

    # This test checks if a user earns 5 points for their first login within 
    # a 24-hour period. 
    # 
    # It also checks if the user receives a notification about earning these points.
    def testUserEarnsPointsIfFirstLogin(self):
        self.user.lastLogin = timezone.make_aware(datetime.now() - timedelta(days=1))
        self.user.save()
        userPointsBefore = Points.objects.get(user=self.user).pointsNum
        self.client.post(self.url, self.input)
        userPointsAfter = Points.objects.get(user=self.user).pointsNum

        # Check if user points have increased
        self.assertEqual(userPointsAfter, userPointsBefore+5)

        # Check if user received points notification
        notification = Notification.objects.filter(toUser=self.user).latest('createdAt')
        self.assertEqual(notification.title, "New Points Earned!")
        self.assertEqual(notification.message, "5 points earned for daily login")