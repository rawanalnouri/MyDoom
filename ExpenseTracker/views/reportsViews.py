"""Views for displaying reports or analytics."""
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from ExpenseTracker.models import Points, House, Category
from ExpenseTracker.forms import ReportForm
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from ExpenseTracker.helpers.reportsHelpers import createArraysData
from .helpers import generateGraph


class HomeView(LoginRequiredMixin, View):
    '''View that handles and shows the Home page to the user.'''

    def get(self, request):
        categories = []
        totalSpent = []

        for category in Category.objects.filter(users__in=[request.user]):
            categories.append(str(category))
            # calculate total spent this month per category
            categoryExpenseThisMonth = 0.0
            today = datetime.now()
            for expense in category.expenditures.filter(date__month=today.month):
                    categoryExpenseThisMonth += float(expense.amount)
            totalSpent.append(round(categoryExpenseThisMonth, 2))

        houses =[]
        pointTotals = []
        for house in House.objects.all():
            houses.append(house.name)
            pointTotals.append(house.points)
        dict = generateGraph(categories, totalSpent,'pie')
        dict.update(generateGraph(houses, pointTotals,'doughnut', 2))

        context = {**dict, **{
            'month': datetime.now().strftime('%B'),
            'year': datetime.now().strftime('%Y'),
            'points': Points.objects.get(user=request.user),
        }}

        return render(request, "home.html", context)
    

class ScoresView(LoginRequiredMixin, ListView):
    '''View that handles and shows the Scores page to the user.'''

    model = Points
    template_name = "scores.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orderedPoints = Points.objects.all().order_by('-count')
        paginator = Paginator(orderedPoints, self.paginate_by)
        pageNumber = self.request.GET.get('page')
        context['houses'] = House.objects.order_by('-points')
        context['userPoints'] = paginator.get_page(pageNumber)
        context['topPoints'] = orderedPoints[:4]
        return context


class ReportsView(LoginRequiredMixin, View):
    '''View that handles and shows the Reports page to the user.'''

    def get(self, request):
        form = ReportForm(user=request.user)
        graphData = generateGraph([], [], 'bar')
        graphData.update({"form": form, "text": "Waiting for your selection..."})
        return render(request, "reports.html", graphData)

    def post(self, request):
        today = datetime.now()
        form = ReportForm(request.POST, user=request.user)
        categories = []
        totalSpent = []
        createdArrays = []
        if form.is_valid():
            timePeriod = form.cleaned_data.get('timePeriod')
            selectedCategories = form.cleaned_data.get('selectedCategory')

            createdArrays = createArraysData(selectedCategories, timePeriod)
            categories = createdArrays[0]
            totalSpent = createdArrays[1]

            graphData = generateGraph(categories, totalSpent, 'bar')
            graphData.update({"form": form, "text": f"An overview of your spending within the last {timePeriod}."})

            # generate a graph for historical data
            first_day_this_month = today.replace(day=1)
            first_day_next_month = (first_day_this_month + timedelta(days=32)).replace(day=1)
            first_day_twelve_months_ago = first_day_next_month - relativedelta(years=1)
            data1 = createArraysData(selectedCategories, timePeriod, first_day_twelve_months_ago,  [365, 52, 12])

            graphData.update({'data1':data1})
            graphData.update({'text2':"Comparison to average over last 12 months"})

            six_months_ago = today + relativedelta(months=-6)
            data2 = createArraysData(selectedCategories, timePeriod, six_months_ago,  [180, 24, 6])

            graphData.update({'data2':data2})
            graphData.update({'text2':f"Compare your average spendings per {timePeriod} in the past"})

            three_months_ago = today + relativedelta(months=-3)
            data3 = createArraysData(selectedCategories, timePeriod, three_months_ago,  [90, 12, 3])

            graphData.update({'data3':data3})
            graphData.update({'text3':f"Your average spending per {timePeriod}"})

            return render(request, "reports.html", graphData)
        else:
            graphData = generateGraph(categories, totalSpent, 'bar')
            graphData.update({"form": form, "text": "Waiting for your selection..."})
            return render(request, "reports.html", graphData)