"""Tests of the log in view."""
from walletwizard.models import User, Points, Notification
from walletwizard.forms import LogInForm
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from walletwizard.tests.testHelpers import *

class LoginViewTest(TestCase, LogInTester):
    """Tests of the log in view."""

    fixtures = ['walletwizard/tests/fixtures/defaultObjects.json']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.url = reverse('logIn')

    def testLogInUrl(self):
        self.assertEqual(self.url, '/logIn/')

    def testGetLogIn(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logIn.html')
        loginForm = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(loginForm, LogInForm))
        self.assertFalse(loginForm.is_bound) 
        self.assertFalse(next)
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages),0)

    def testGetLogInWithRedirect(self):
        destinationUrl = reverse('scores')
        self.url = reverse_with_next('logIn', destinationUrl)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logIn.html')
        form = response.context['form']
        next = response.context['next']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertEqual(next, destinationUrl)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 0)
    
    def testGetLogInRedirectsWhenLoggedIn(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url, follow=True)
        redirectUrl = reverse('home')
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def testUnsuccessfulLogIn(self):
        formInput = { 'username': self.user.username, 'password': 'WrongPassword123' }
        response = self.client.post(self.url, formInput)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logIn.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(self.isUserLoggedIn())
        # check for error message
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages),1)
        self.assertEqual(listOfMessages[0].level, messages.ERROR)
    
    def testLogInWithBlankUsername(self):
        formInput = { 'username': '', 'password': self.user.password }
        response = self.client.post(self.url, formInput)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logIn.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self.isUserLoggedIn())
        # check for error message
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages),1)
        self.assertEqual(listOfMessages[0].level, messages.ERROR)

    def testLogInWithBlankPassword(self):
        formInput = { 'username': self.user.username, 'password': '' }
        response = self.client.post(self.url, formInput)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logIn.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self.isUserLoggedIn())
        # check for error message
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages),1)
        self.assertEqual(listOfMessages[0].level, messages.ERROR)

    def testSuccessfulLogIn(self):
        formInput = { 'username': 'testuser', 'password': 'Password123' }
        response = self.client.post(self.url, formInput, follow=True)
        self.assertTrue(self.isUserLoggedIn())
        userRedirect = reverse('home')
        self.assertRedirects(response, userRedirect, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        # check for no error messages
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages), 0)
    
    def testSuccesfulLogInWithRedirect(self):
        redirectUrl = reverse('scores')
        formInput = { 'username': 'testuser', 'password': 'Password123', 'next': redirectUrl }
        response = self.client.post(self.url, formInput, follow=True)
        self.assertTrue(self.isUserLoggedIn())
        self.assertRedirects(response, redirectUrl, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'scores.html')
        # check for no error messages
        listOfMessages = list(response.context['messages'])
        self.assertEqual(len(listOfMessages), 0)

    def testPostLogInRedirectsWhenLoggedIn(self):
        self.client.force_login(self.user)
        formInput = { 'username': 'wronguser', 'password': 'WrongPassword123' }
        response = self.client.post(self.url, formInput, follow=True)
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def testUserEarnsPointsIfFirstLogin(self):
        self.user.lastLogin = timezone.make_aware(datetime.now() - timedelta(days=1))
        self.user.save()
        userPointsBefore = Points.objects.get(user=self.user).count
        formInput = { 'username': 'testuser', 'password': 'Password123' }
        self.client.post(self.url, formInput)
        userPointsAfter = Points.objects.get(user=self.user).count
        # Check if user points have increased
        self.assertEqual(userPointsAfter, userPointsBefore + 5)
        # Check if user received points notifications
        notifications = Notification.objects.filter(toUser=self.user).order_by('-createdAt')[:2]
        titles=getNotificationTitles(notifications)
        messages=getNotificationMessages(notifications)
        self.assertIn("House points gained!", titles)
        self.assertIn(str(self.user.house.name) + " has gained 5 points", messages)
        self.assertIn("New Points Earned!", titles)
        self.assertIn("5 points earned for daily login", messages)
    
    def testPostLogInWithIncorrectCredentialsAndRedirect(self):
        redirectUrl = reverse('scores')
        formInput = { 'username': self.user.username, 'password': 'WrongPassword123', 'next': redirectUrl }
        response = self.client.post(self.url, formInput)
        next = response.context['next']
        self.assertEqual(next, redirectUrl)

    def testLogInProhibitedWhenLoggedIn(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logIn'))
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('home.html')