from django.shortcuts import render, redirect, reverse
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, DetailView
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LogInForm
from django.http import HttpResponse
from django.http import Http404
from .models import *
from .forms import *
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

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

        categories = []
        totalSpent = []
        categorySpend = 0
        for category in Category.objects.filter(id = kwargs['categoryId'], user=self.request.user):
            # all categories
            categories.append(str(category))
            categories.append("Remaining Budget")
            # total spend per catagory
            categorySpend = 0.00
            for expence in category.expenditures.all():
                categorySpend += float(expence.amount)
            totalSpent.append(categorySpend)
            totalSpent.append(float(category.spendingLimit.getNumber()) - categorySpend)

        dict = generateGraph(categories, totalSpent, 'doughnut')
        dict.update(context)

        # analysis stuff
        namesOfExpenses = []
        currentCategory = Category.objects.filter(id = kwargs['categoryId'], user=self.request.user)
        allExpensesInRange = category.expenditures.all().filter(date__year='2023', date__month='01')
        # filter between months
        # Sample.objects.filter(date__range=["2011-01-01", "2011-01-31"])
        for expense in allExpensesInRange:
            namesOfExpenses.append(expense.title)

        dict.update({'stuff': namesOfExpenses})

        return render(request, self.template_name, dict)

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


class SignUpView(View):
    def get(self, request, *args, **kwargs):
        signUpForm = SignUpForm()
        return render(request, 'signUp.html', {'form': signUpForm})

    def post(self, request, *args, **kwargs):
        signUpForm = SignUpForm(request.POST)
        if signUpForm.is_valid():
            user = signUpForm.save()
            login(request, user)
            return redirect('home')
        return render(request, 'signUp.html', {'form': signUpForm})

class LogInView(View):
    def get(self, request, *args, **kwargs):
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
                return redirect('home')
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return render(request, 'logIn.html', {"form": form})

class LogOutView(LoginRequiredMixin, View):
    login_url = reverse_lazy('logIn')

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('index')

class IndexView(View):

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
                totalSpent.append(categorySpend/float(category.spendingLimit.getNumber())*100)

            return render(request, "home.html", generateGraph(categories, totalSpent, 'polarArea'))



'''Implements a view for handling requests to the reports page'''
def reportsView(request):

    # login_url = reverse_lazy('logIn')
    categories = []
    totalSpent = []

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            timePeriod = form.cleaned_data.get('timePeriod')
            selectedCategory = form.cleaned_data.get('selectedCategory')

            for selected in selectedCategory:
                category = Category.objects.get(name=selected)
                # all categories
                categories.append(selected)
                # total spend per catagory
                categorySpend = 0.00
                for expence in category.expenditures.all():
                    categorySpend += float(expence.amount)
                totalSpent.append(categorySpend/float(category.spendingLimit.getNumber())*100)

            dict = generateGraph(categories, totalSpent, 'bar')
            dict.update({"form": form})

            return render(request, "reports.html", dict)

    form = ReportForm()
    dict = generateGraph(categories, totalSpent, 'bar')
    dict.update({"form": form})
    return render(request, "reports.html", dict)

    # def get(self, request):
    #     categories = []
    #     totalSpent = []
    #     for category in Category.objects.filter(user=self.request.user):
    #         # all categories
    #         categories.append(str(category))
    #         # total spend per catagory
    #         categorySpend = 0.00
    #         for expence in category.expenditures.all():
    #             categorySpend += float(expence.amount)
    #         totalSpent.append(categorySpend/float(category.spendingLimit.getNumber())*100)
    #
    #     return render(request, "reports.html", generateGraph(categories, totalSpent, 'bar'))
    #
    #     return render(request, 'reports.html', generateGraph(["a","b","c"], [1,1,2], 'polarArea'))




class ShowUserView(LoginRequiredMixin, DetailView):
    """View that shows individual user details."""

    model = User
    template_name = 'showUser.html'
    context_object_name = "user"
    pk_url_kwarg = 'user_id'
    login_url = reverse_lazy('logIn')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Generate content to be displayed in the template."""

        context = super().get_context_data(*args, **kwargs)
        user = self.get_object()
        context['following'] = self.request.user.isFollowing(user)
        context['followable'] = (self.request.user != user)
        return context

    def get(self, request, *args, **kwargs):
        """Handle get request, and redirect to users if user_id invalid."""

        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect(reverse('users'))


class FollowToggleView(LoginRequiredMixin, View):
    '''View that handles follow/unfollow user functionality'''

    login_url = reverse_lazy('logIn')

    def get(self, request, userId, *args, **kwargs):
        currentUser = request.user
        try:
            followee = User.objects.get(id=userId)
            currentUser.toggleFollow(followee)
        except ObjectDoesNotExist:
            return redirect('users')
        else:
            return redirect('showUser', user_id=userId)


class ProfileView(LoginRequiredMixin, View):
    '''View that handles requests to the profile page'''

    login_url = reverse_lazy('logIn')

    def get(self, request):
        return render(request,'profile.html')


class EditProfileView(LoginRequiredMixin, View):
    '''View that handles requests to the edit profile page'''

    login_url = reverse_lazy('logIn')

    def get(self,request):
        newForm = EditProfile(instance=request.user)
        return render(request, "editProfile.html", {'form': newForm})

    def post(self,request):
        form = EditProfile(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        else:
            return render(request, "editProfile.html", {'form': form})


class ChangePassword(LoginRequiredMixin, PasswordChangeView, View):
    '''View that changes the user's password'''

    form_class = ChangePasswordForm
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('home')


class UserListView(LoginRequiredMixin, ListView):
    '''View that shows a list of all users and allows user to filter users based on username'''

    model = User
    template_name = 'users.html'
    context_object_name = 'users'
    paginate_by = 9 # Show 9 users per page

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query is None:
            objectList = User.objects.all()
        else: 
            objectList = User.objects.filter(
                Q(username__istartswith=query)
            )
        return objectList

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        users = paginator.get_page(page)
        context['users'] = users
        return context
