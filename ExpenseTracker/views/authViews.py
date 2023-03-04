from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from ..forms import SignUpForm, LogInForm
from django.utils.timezone import datetime
from ExpenseTracker.models import *
from ExpenseTracker.forms import *
from .helpers import addPoints
from datetime import datetime

class SignUpView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'home.html')
        else:
            signUpForm = SignUpForm()
            return render(request, 'signUp.html', {'form': signUpForm})

    def post(self, request, *args, **kwargs):
        signUpForm = SignUpForm(request.POST)
        if signUpForm.is_valid():
            user = signUpForm.save()
            pointsObject = Points()
            pointsObject.user=user
            pointsObject.pointsNum=50
            pointsObject.save()
          
            login(request, user)
            return redirect('home')
        return render(request, 'signUp.html', {'form': signUpForm})


class LogInView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, 'home.html')
        else:
            form = LogInForm()
            return render(request, 'logIn.html', {"form": form})

    def post(self, request, *args, **kwargs):
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                if user.last_login.date() != datetime.now().date():
                    # if this is the first login of the day, add 5 points
                    addPoints(request, 5)

                return redirect('home') 

        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return render(request, 'logIn.html', {"form": form})


class LogOutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('index')

    def handle_no_permission(self):
        return redirect('logIn')


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'home.html')
        else:
            return render(request, 'index.html')