from django.shortcuts import render, redirect
from django.views import View
from .forms import CategoryForm

class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')

class ReportsView(View):
    def get(self, request):
        return render(request, 'reports.html')
