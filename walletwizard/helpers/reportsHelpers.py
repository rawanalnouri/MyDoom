'''Helper file containing methods to generate graph data for reports.'''

from datetime import datetime
from datetime import timedelta
from walletwizard.models import Category

# Constants used in calculations.
DAYS_PER_WEEK = 7
DAYS_PER_MONTH = 30
DAYS_PER_YEAR = 365
WEEKS_PER_MONTH = 4
WEEKS_PER_YEAR = 52
MONTHS_PER_YEAR = 12

'''Spending Limit (Budget) Calculations'''

def convertBudgetToDaily(category):
    '''Convert the category's spending limit into a daily spending limit.'''

    currentTimePeriod = category.spendingLimit.timePeriod
    amount = category.spendingLimit.getNumber()

    if currentTimePeriod == 'weekly':
        return amount / DAYS_PER_WEEK
    elif currentTimePeriod == 'monthly':
        return amount / DAYS_PER_MONTH
    elif currentTimePeriod == 'yearly':
        return amount / DAYS_PER_YEAR
    else:
        return amount

def convertBudgetToWeekly(category):
    '''Convert the category's spending limit into a weekly spending limit.'''

    currentTimePeriod = category.spendingLimit.timePeriod
    amount = category.spendingLimit.getNumber()

    if currentTimePeriod == 'daily':
        return amount * DAYS_PER_WEEK
    elif currentTimePeriod == 'monthly':
        return amount / WEEKS_PER_MONTH
    elif currentTimePeriod == 'yearly':
        return amount / WEEKS_PER_YEAR
    else:
        return amount

def convertBudgetToMonthly(category):
    '''Convert the category's spending limit into a weekly spending limit.'''
    
    currentTimePeriod = category.spendingLimit.timePeriod
    amount = category.spendingLimit.getNumber()

    if currentTimePeriod == 'daily':
        return amount * DAYS_PER_MONTH
    elif currentTimePeriod == 'weekly':
        return amount * WEEKS_PER_MONTH
    elif currentTimePeriod == 'yearly':
        return amount / MONTHS_PER_YEAR
    else:
        return amount
    
'''Data and Label generation for reports page graphs.'''

def createDataAndLabelArrays(categories, timePeriod):
    '''Create 2 arrays (graph data points as well as their labels). The data consists of the expenditures
    within the last 'day', 'week', or 'month', according to the user's choice.'''

    today = datetime.now()
    names = []
    data =[]
    filteredCategories=''
    for selected in categories:
        category = Category.objects.get(id=selected)
        budgetCalculated = category.spendingLimit.getNumber()

        categorySpend = 0.00
        names.append(category.name)

        if timePeriod == 'day':
            # filtering all expenditures within the previous day
            budgetCalculated = convertBudgetToDaily(category)
            yesterday = today - timedelta(days=1)
            filteredCategories = category.expenditures.filter(date__gte=yesterday)

        if timePeriod == 'week':
            # filtering all expenditures within the previous week
            budgetCalculated = convertBudgetToWeekly(category)
            weekStart = today
            weekStart -= timedelta(days=weekStart.weekday())
            weekEnd = today + timedelta(days = 1)
            filteredCategories = category.expenditures.filter(date__gte=weekStart, date__lt=weekEnd)

        if timePeriod == 'month':
            # filtering all expenditures within the previous month
            budgetCalculated = convertBudgetToMonthly(category)
            filteredCategories = category.expenditures.filter(date__month=today.month, date__year=today.year)

        for expense in filteredCategories:
            categorySpend += float(expense.amount)

        # adding the percentage each category's used budget, capped at 100%
        amount = categorySpend/float(budgetCalculated)*100
        if amount < 100:
            data.append(round(amount,2))
        else:
            data.append(100)

    returnedArrays = []
    returnedArrays.append(names)
    returnedArrays.append(data)
    return returnedArrays


def createDataAverageArrays(categories, timePeriod, pastMonthsFilterApplied, numberOfDaysWeeksMonthsArray):
    '''Generate a single array. Data calculations are made according to user's choice of whether they want 
    a mean analysis of 'daily', 'weekly', or 'monthly' ependitures.'''

    data = []
    filteredCategories=''

    for selected in categories:
        category = Category.objects.get(id=selected)
        budgetCalculated = category.spendingLimit.getNumber()

        categorySpend = 0.00
        # category expenditures are filtered and then their total is calculated
        filteredCategories = category.expenditures.filter(date__gte=pastMonthsFilterApplied)
        for expense in filteredCategories:
            categorySpend += float(expense.amount)

        if timePeriod == 'day':
            # average spending per day is calculated
            budgetCalculated = convertBudgetToDaily(category)
            days = numberOfDaysWeeksMonthsArray[0]
            categorySpend = categorySpend/days

        if timePeriod == 'week':
            # average spending per week is calculated
            budgetCalculated = convertBudgetToWeekly(category)
            # for the filtered smaller graphs, the average spending per week is calculated
            weeks = numberOfDaysWeeksMonthsArray[1]
            categorySpend = categorySpend/weeks

        if timePeriod == 'month':
            # average spending per month is calculated
            budgetCalculated = convertBudgetToMonthly(category)
            # for the filtered smaller graphs, the average spending per month is calculated
            months = numberOfDaysWeeksMonthsArray[2]
            categorySpend = categorySpend/months

        # capping the maximum data to 100%
        amount = categorySpend/float(budgetCalculated)*100
        if amount < 100:
            data.append(round(amount,2))
        else:
            data.append(100)

    return data