from django.shortcuts import render, redirect, reverse
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.db.utils import IntegrityError

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import User
from .forms import SignUpForm, LogInForm

from .forms import CategorySpendingLimitForm, ExpenditureForm
from .models import Category

class CategoryView(TemplateView):
    template_name = 'category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ExpenditureForm()
        category = Category.objects.get(name=self.kwargs['category_name'])
        context['category'] = category
        return context
    
    def post(self, request, *args, **kwargs):
        form = ExpenditureForm(request.POST)
        if form.is_valid():
            category = Category.objects.get(name=kwargs['category_name'])
            form.save(category)
        return redirect(reverse('category', args=[category.name]))

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategorySpendingLimitForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            form.save()
        except IntegrityError:
            messages.add_message(self.request, messages.ERROR, "Failed to Create Category. Please ensure the start date is before the end date.")
            return redirect('create_category')
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
            #Users redirected to their custom home page
            login(request,user)
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

''' Logs out a logged in user '''
@login_required(login_url='/logIn/')
def logOut(request):
    logout(request)
    return redirect('index')


class IndexView(View):
    def get(self, request):
            return render(request, 'index.html')

class HomeView(View):
    def get(self, request):
        return render(request, "home.html")

class ReportsView(View):
    def get(self, request):
        return render(request, 'reports.html')
