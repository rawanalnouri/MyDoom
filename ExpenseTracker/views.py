from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User
from django.urls import reverse
from .forms import SignUpForm, LogInForm


def homePage(request):
    return render(request, "home.html")

def signUp(request):
    if request.method == 'POST':
        signUpForm = SignUpForm(request.POST)
        if(signUpForm.is_valid()):
            user = signUpForm.save()
            #Users redirected to their custom landing page
            login(request,user)

            redirectLocation = reverse('landingPage', kwargs={'user_id': request.user.id})
            return redirect(redirectLocation) 

    else:
        signUpForm = SignUpForm()
    return render(request,'signUp.html', {'form': signUpForm})

def logIn(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password) 
            if user is not None:
                login(request, user) 
                redirectLocation = reverse('landingPage', kwargs={'user_id': user.id})
                return redirect(redirectLocation) 


        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")

    form = LogInForm()
    return render(request, 'logIn.html', {"form": form})

''' Logs out a logged in user '''
@login_required(login_url='/logIn/')
def logOut(request):
    logout(request)
    return redirect('homePage')

''' Logs in an authenticated user and takes them to their landing page'''
@login_required(login_url='/logIn/')
def landingPage(request, user_id):
    if request.user.is_authenticated:
        client = User.objects.get(id = user_id)
        return render(request, "landingPage.html", {'user':client})
    return render(request, "home.html")