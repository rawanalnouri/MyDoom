from django.shortcuts import render, redirect, reverse
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LogInForm
from django.http import HttpResponse
from .forms import CategorySpendingLimitForm, ExpenditureForm
from .models import Category, Expenditure
from django.core.paginator import Paginator

import random
import datetime
import time


class CategoryView(LoginRequiredMixin, TemplateView):
    '''Implements a template view for displaying a specific category and handling create expenditure form submissions'''
    '''Handles editing categories'''
    
    template_name = 'category.html'
    login_url = reverse_lazy('logIn') #redirects to the "logIn" path if the user is not logged in

    def get(self, request, *args, **kwargs):
        context = {}
        category = Category.objects.filter(id = kwargs['categoryId'], user=self.request.user).first()
        #Forms used for modal pop-ups
        context['expenditureForm'] = ExpenditureForm()
        context['categoryForm'] = CategorySpendingLimitForm(user=self.request.user, instance = category)
        context['category'] = category
        # adding pagination
        paginator = Paginator(category.expenditures.all(), 15) # Show 15 expenditures per page
        page = self.request.GET.get('page')
        expenditures = paginator.get_page(page)
        context['expenditures'] = expenditures
        return render(request, self.template_name, context)

    ''' Handles saving a valid form and presenting error messages '''
    def handleForm(self, form, category, errorMessage, successMessage):
        if category and form.is_valid():
            messages.add_message(self.request, messages.SUCCESS, successMessage)
            form.save(category)
        else:
            messages.add_message(self.request, messages.ERROR, errorMessage)
    
    def post(self, request, *args, **kwargs):
        category = Category.objects.filter(id = kwargs['categoryId'], user=self.request.user).first()
        expendForm = ExpenditureForm(request.POST)
        categForm = CategorySpendingLimitForm(request.POST, user=self.request.user, instance=category) 

        if 'expenditureForm' in request.POST:
            self.handleForm(expendForm, category, "Failed to Create Expenditure", "Successfully Created Expenditure")

        elif 'categoryForm' in request.POST:
            self.handleForm(categForm, category, "Failed to Updated Category", "Successfully Updated Category")

        #Using hidden id to determine which form is being used and adding to context
        context = {
            'expenditureForm': expendForm,
            'categoryForm': categForm
        }
        return redirect(reverse('category', args=[category.id]), context=context)

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
        return redirect(reverse('category', args=[category.id]))
    
    def form_invalid(self, form):
        for error in form.non_field_errors():
            messages.add_message(self.request, messages.ERROR, error)
        return super().form_invalid(form)

class CategoryDeleteView(LoginRequiredMixin, View):
    '''Implements a view for deleting an expenditure'''
    login_url = reverse_lazy('logIn')

    def dispatch(self, request, *args, **kwargs):
        category = Category.objects.filter(id = kwargs['categoryId'], user=self.request.user).first()
        categoryExpenditures = category.expenditures.all()
        for expenditure in categoryExpenditures:
            expenditure.delete()
        category.spendingLimit.delete()
        category.delete()
        messages.add_message(request, messages.SUCCESS, "Expenditure successfully deleted")
        return redirect('home')

class ExpenditureUpdateView(LoginRequiredMixin, View):
    '''Implements a view for updating an expenditure and handling update expenditure form submissions'''
    login_url = reverse_lazy('logIn')

    def get(self, request, *args, **kwargs):
        expenditure = Expenditure.objects.filter(id=kwargs['expenditureId']).first()
        form = ExpenditureForm(instance=expenditure)
        return render(request, 'partials/bootstrapForm.html', {'form': form})
    
    def post(self, request, *args, **kwargs):
        expenditure = Expenditure.objects.filter(id=kwargs['expenditureId']).first()
        form = ExpenditureForm(instance=expenditure, data=request.POST)
        if form.is_valid():
            category = Category.objects.filter(id=kwargs['categoryId'], user=request.user).first()
            form.save(category)
            messages.add_message(request, messages.SUCCESS, "Successfully Updated Expenditure")
            return redirect(reverse('category', args=[kwargs['categoryId']]))
        else:
            messages.add_message(request, messages.ERROR, "Failed to Update Expenditure")
            return render(request, 'partials/bootstrapForm.html', {'form': form})


class ExpenditureDeleteView(LoginRequiredMixin, View):
    '''Implements a view for deleting an expenditure'''
    login_url = reverse_lazy('logIn')

    def dispatch(self, request, *args, **kwargs):
        expenditure = Expenditure.objects.get(id=kwargs['expenditureId'])
        expenditure.delete()
        messages.add_message(request, messages.SUCCESS, "Expenditure successfully deleted")
        return redirect(reverse('category', args=[kwargs['categoryId']]))


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
            categories = []

            totalSpent = []

            for category in Category.objects.filter(user=self.request.user):

                # all categories

                categories.append(str(category))

                # total spend per catagory

                categorySpend = 0.00

                for expence in category.expenditures.all():
                    categorySpend += float(expence.amount)

                totalSpent.append(categorySpend/float(category.spending_limit.getNumber())*100)


            return render(request, "home.html", generateGraph(categories, totalSpent, 'polarArea'))



class ReportsView(LoginRequiredMixin, View):
    '''Implements a view for handling requests to the reports page'''

    login_url = reverse_lazy('logIn')

    def get(self, request):
        return render(request, 'reports.html')