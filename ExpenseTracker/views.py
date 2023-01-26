from django.shortcuts import render
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CategorySpendingLimitForm
from .models import Category

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategorySpendingLimitForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')

class ReportsView(View):
    def get(self, request):
        return render(request, 'reports.html')
