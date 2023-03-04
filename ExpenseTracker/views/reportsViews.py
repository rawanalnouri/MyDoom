from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from ExpenseTracker.models import *
from ExpenseTracker.forms import *
from .helpers import generateGraph

class HomeView(LoginRequiredMixin, View):
    '''Implements a view for handling requests to the home page'''

    def get(self, request):
        categories = []
        totalSpent = []
        for category in Category.objects.filter(users__in=[request.user]):
            # all categories
            categories.append(str(category))
            # total spend per catagory
            categorySpend = 0.00
            for expence in category.expenditures.all():
                categorySpend += float(expence.amount)
            totalSpent.append(categorySpend/float(category.spendingLimit.getNumber())*100)

        return render(request, "home.html", generateGraph(categories, totalSpent, 'polarArea'))
    
    def handle_no_permission(self):
        return redirect('logIn')
    

def reportsView(request):
    '''Implements a view for handling requests to the reports page'''

    categories = []
    totalSpent = []

    if request.method == 'POST':
        form = ReportForm(request.POST, user=request.user)
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

    form = ReportForm(user=request.user)
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