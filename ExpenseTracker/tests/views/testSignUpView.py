from ExpenseTracker.models import User 
from ExpenseTracker.forms import SignUpForm
from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from ExpenseTracker.tests.helpers import LogInTester

#tests for the sign up view

class SignUpViewTest(TestCase, LogInTester):
    fixtures = ['ExpenseTracker/tests/fixtures/defaultObjects.json']


    def setUp(self):
        self.url = reverse('signUp')
        self.input = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'username': 'jane123',
            'email': 'janedoe@test.org',
            'newPassword': "Password123",
            'passwordConfirmation': "Password123"
        }
        self.form = SignUpForm(data = self.input)

    # This test checks whether the URL for the sign-up view is correct. 
    # 
    # It asserts that the url attribute is equal to '/signUp/'.
    def testUrl(self):
        self.assertEqual('/signUp/', self.url)

    # This test checks that a user who is not logged in can 
    # access the sign-up page successfully. 
    # 
    # It sends a GET request to the sign-up URL 
    # and asserts that the response status code is 200. 
    # It also checks that the 'signUp.html' template 
    # is used and that the form used to sign up is an instance 
    # of the SignUpForm class.
    def testGetSignUpIfUserNotAuthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signUp.html')
        signUpForm = response.context['form']
        self.assertTrue(isinstance(signUpForm,SignUpForm))

    # This test checks that if a user is already logged in, 
    # they will be redirected to the home page if they try to 
    # access the sign-up page. 
    # 
    # It logs in a user using the force_login() method,
    # then sends a GET request to the sign-up URL and 
    # asserts that the response redirects to the home page.
    def testRedirectToHomeIfUserAuthenticated(self):
        # User should be taken to the home page if logged in
        user = User.objects.get(id=1)
        self.client.force_login(user)
        response = self.client.get(self.url)
        userHomePage = reverse('home')
        self.assertRedirects(response, userHomePage, status_code=302, target_status_code=200)

    # This test checks that an unsuccessful sign-up attempt will
    #  not create a new user. 
    # 
    # It modifies the input data to make the sign-up attempt invalid 
    # (in this case, by providing an invalid email address). 
    # It then sends a POST request to the sign-up URL and asserts 
    # that no new users were created. It also checks that the 
    # response status code is 200, that the 'signUp.html' template is used,
    # and that the form used to sign up is an instance of the SignUpForm class.
    def testUnsuccessfulSignUp(self):
        self.input['email'] = 'email!'
        totalUsersBefore = User.objects.count()
        response = self.client.post(self.url, self.input)
        totalUsersAfter = User.objects.count()
        self.assertEqual(totalUsersBefore, totalUsersAfter)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'signUp.html')
        form = response.context['form']
        self.assertTrue(isinstance(form,SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self.isUserLoggedIn())

    # This test checks that a successful sign-up attempt will create
    #  a new user and redirect them to the home page. 
    # 
    # It sends a POST request to the sign-up URL with valid input data, 
    # then asserts that a new user was created. It also checks that the
    # user's data was saved correctly, that the response redirects to 
    # the home page, and that the 'home.html' template is used.
    def testSuccessfulSignUpAndRedirect(self):
        totalUsersBefore = User.objects.count()
        response = self.client.post(self.url, self.input, follow=True)
        totalUsersAfter = User.objects.count()
        self.assertEqual(totalUsersBefore+1, totalUsersAfter)

        #Check data saved correctly
        newSignedUpUser = User.objects.get(email='janedoe@test.org')
        self.assertEqual(newSignedUpUser.firstName, 'Jane')
        self.assertEqual(newSignedUpUser.lastName,'Doe')
        self.assertTrue(check_password('Password123',newSignedUpUser.password))
        self.assertTrue(self.isUserLoggedIn())

        #Check Redirects
        userHomePage = reverse('home')
        self.assertRedirects(response, userHomePage, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, "home.html")