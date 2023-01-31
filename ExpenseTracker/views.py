from django.shortcuts import render, redirect, reverse
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.db.utils import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LogInForm

from .forms import CategorySpendingLimitForm, ExpenditureForm
from .models import Category
from django.core.paginator import Paginator

import random
import datetime
import time


class CategoryView(LoginRequiredMixin, TemplateView):
    '''Implements a template view for displaying a specific category and handling expenditure form submissions'''

    template_name = 'category.html'
    login_url = reverse_lazy('logIn') #redirects to the "logIn" path if the user is not logged in

    def get(self, request, *args, **kwargs):
        context = {}
        context['form'] = ExpenditureForm()
        category = Category.objects.filter(name=kwargs['categoryName'], user=self.request.user).first()
        context['category'] = category
        # adding pagination
        paginator = Paginator(category.expenditures.all(), 15) # Show 15 expenditures per page
        page = self.request.GET.get('page')
        expenditures = paginator.get_page(page)
        context['expenditures'] = expenditures
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = ExpenditureForm(request.POST)
        category = Category.objects.filter(name=kwargs['categoryName'], user=self.request.user).first()
        if category and form.is_valid():
            messages.add_message(self.request, messages.SUCCESS, "Successfully Created Expenditure")
            form.save(category)
        else:
            messages.add_message(self.request, messages.ERROR, "Failed to Create Expenditure")
        return redirect(reverse('category', args=[category.name]))


class CategoryCreateView(LoginRequiredMixin, CreateView):
    '''Implements a view for creating a new category using a form'''

    model = Category
    form_class = CategorySpendingLimitForm
    template_name = 'categoryForm.html'
    login_url = reverse_lazy('logIn')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        category = form.save()
        messages.add_message(self.request, messages.SUCCESS, "Successfully Created Category")
        return redirect(reverse('category', args=[category.name]))

    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.add_message(self.request, messages.ERROR, error)
        return super().form_invalid(form)


def signUp(request):
    if request.method == 'POST':
        signUpForm = SignUpForm(request.POST)
        if(signUpForm.is_valid()):
            user = signUpForm.save()
            login(request, user)
            return redirect('home')

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
                return redirect('home')

        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")

    form = LogInForm()
    return render(request, 'logIn.html', {"form": form})


@login_required(login_url='/logIn/')
def logOut(request):
    logout(request)
    return redirect('index')


class IndexView(View):


    # queryset = City.objects.order_by('-population')[:5]
    # for city in queryset:
    #     labels.append(city.name)
    #     data.append(city.population)

    def get(self, request):
            return render(request, 'index.html')

def generateGraph(categories, spentInCategories, type):
    dict = {'labels': categories, 'data': spentInCategories, 'type':type}
    return dict

class HomeView(LoginRequiredMixin, View):
    '''Implements a view for handling requests to the home page'''

    login_url = reverse_lazy('logIn')

    def get(self, request):
        return render(request, "home.html", generateGraph(["a", "b", "c"], [2, 1, 5], 'polarArea'))


class ReportsView(LoginRequiredMixin, View):
    '''Implements a view for handling requests to the reports page'''

    login_url = reverse_lazy('logIn')

    def get(self, request):
        return render(request, 'reports.html')
