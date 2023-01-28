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

class CategoryView(LoginRequiredMixin, TemplateView):
    '''Implements a template view for displaying a specific category and handling expenditure form submissions'''

    template_name = 'category.html'
    login_url = reverse_lazy('logIn') #redirects to the "logIn" path if the user is not logged in

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ExpenditureForm()
        category = Category.objects.filter(name=self.kwargs['category_name'], user=self.request.user).first()
        context['category'] = category
        return context
    
    def post(self, request, *args, **kwargs):
        form = ExpenditureForm(request.POST)
        category = Category.objects.filter(name=kwargs['category_name'], user=self.request.user).first()
        if category and form.is_valid():
            messages.add_message(self.request, messages.SUCCESS, "Successfully Created Expenditure")
            form.save(category)
        else:
            messages.add_message(self.request, messages.ERROR, "Failed to Create Expenditure")
            return redirect(reverse('home'))
        return redirect(reverse('category', args=[category.name]))


class ExpenditureCreateView(View):
    '''Implements a view for creating a new expenditure using a form'''

    def get(self, request, *args, **kwargs):
        categoryName = kwargs.get('categoryName')
        context = {'categoryName': categoryName}
        return render(request, 'modals/createExpenditure.html', context)

    def post(self, request, *args, **kwargs):
        form = ExpenditureForm(request.POST)
        category = Category.objects.filter(name=kwargs['categoryName'], user=self.request.user).first()
        if category and form.is_valid():
            messages.add_message(self.request, messages.SUCCESS, "Successfully Created Expenditure")
            form.save(category)
            return redirect(reverse('category', args=[category.name]))
        else:
            messages.add_message(self.request, messages.ERROR, "Failed to Create Expenditure")
            return redirect(reverse('home'))



class CategoryCreateView(LoginRequiredMixin, CreateView):
    '''Implements a view for creating a new category using a form'''
    
    model = Category
    form_class = CategorySpendingLimitForm
    template_name = 'categoryForm.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('logIn')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            form.save()
        except IntegrityError:
            messages.add_message(self.request, messages.ERROR, "Failed to Create Category. Please ensure the start date is before the end date.")
            return redirect('createCategory')
        else:
            messages.add_message(self.request, messages.SUCCESS, "Successfully Created Category")
            return redirect('home')
    
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
    def get(self, request):
            return render(request, 'index.html')


class HomeView(LoginRequiredMixin, View):
    '''Implements a view for handling requests to the home page'''

    login_url = reverse_lazy('logIn')

    def get(self, request):
        return render(request, "home.html")


class ReportsView(LoginRequiredMixin, View):
    '''Implements a view for handling requests to the reports page'''
    
    login_url = reverse_lazy('logIn')

    def get(self, request):
        return render(request, 'reports.html')
