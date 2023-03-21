"""Views for user authentication."""
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login,logout
from walletwizard.models import House
from walletwizard.forms import SignUpForm, LogInForm
from walletwizard.helpers.pointsHelpers import createPoints, updatePoints, housePointsUpdate
from walletwizard.helpers.notificationsHelpers import createBasicNotification
from PersonalSpendingTracker.settings import REDIRECT_URL_WHEN_LOGGED_IN
from django.utils import timezone
from django.utils.timezone import datetime
from datetime import datetime
from .helpers import LoginProhibitedMixin

        
class SignUpView(LoginProhibitedMixin, View):
    """View that signs up user."""

    redirect_when_logged_in_url = REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            signUpForm = SignUpForm()
            return render(request, 'signUp.html', {'form': signUpForm})

    def post(self, request, *args, **kwargs):
        signUpForm = SignUpForm(request.POST)
        if signUpForm.is_valid():
            user = signUpForm.save()
            points = createPoints(user)
            login(request, user)

            createBasicNotification(user, "New Points Earned!", str(points) + " points earned for signing up!")
            createBasicNotification(user, "Welcome to spending trracker!", "Manage your money here and earn points for staying on track!")

            # assign house to new user
            house = House.objects.get(id = (user.id % 4) + 1)
            user.house = house
            user.save()
            house.memberCount += 1
            house.save()
            housePointsUpdate(user, 50)
           
            return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
        return render(request, 'signUp.html', {'form': signUpForm})


class LogInView(LoginProhibitedMixin, View):
    '''View that logs in a user.'''

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request, *args, **kwargs):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request, *args, **kwargs):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or REDIRECT_URL_WHEN_LOGGED_IN
        if form.is_valid():
            user = form.getUser()
            if user is not None:
                login(request, user)
                # add 5 points if first login of the day
                if user.lastLogin.date() != datetime.now().date():
                    updatePoints(user, 5)
                    createBasicNotification(user, "New Points Earned!", "5 points earned for daily login")
                # update user's 'lastLogin'
                user.lastLogin = timezone.now()
                user.save(update_fields=['lastLogin'])
                return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()
    
    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'logIn.html', {"form": form, 'next': self.next})


class LogOutView(LoginRequiredMixin, View):
    '''View that logs a signed-in user out.'''

    def get(self, request):
        logout(request)
        return redirect('index')


class IndexView(LoginProhibitedMixin, View):
    '''View that is displayed to a user before signing in.'''

    redirect_when_logged_in_url = REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return render(request, 'index.html')