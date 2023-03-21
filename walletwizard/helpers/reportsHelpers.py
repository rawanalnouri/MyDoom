''' Helper file containg method to generate data for graphs '''

from datetime import datetime
from datetime import timedelta
from walletwizard.models import *

# constant numbers to use later for calculating averages across time periods
DAYS_PER_WEEK = 7
DAYS_PER_MONTH = 30
DAYS_PER_YEAR = 365
WEEKS_PER_MONTH = 4
WEEKS_PER_YEAR = 52
MONTHS_PER_YEAR = 12


# Converts the user's spending limit into a daily spending limit
def convertBudgetToDaily(category):
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

# Converts the user's spending limit into a weekly spending limit
def convertBudgetToWeekly(category):
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

# Converts the user's spending limit into a monthly spending limit
def convertBudgetToMonthly(category):
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

'''Genrates data for the graphs on the reports page
in the case that no pastMonthsFilterApplied and no numberOfDaysWeeksMonthsArray
is passed means both graph data and labels are being generated for the main
graph, which only looks at data from the previous day, week, and month. The
labels will be reused for the filtered data grsphs so they can be reused instead
of regenerated'''
def createArraysData(categories, timePeriod, pastMonthsFilterApplied=None, numberOfDaysWeeksMonthsArray=''):
    today = datetime.now()
    names = []
    data =[]
    filteredCategories=''

    for selected in categories:
        category = Category.objects.get(id=selected)
        budgetCalculated = category.spendingLimit.getNumber()

        categorySpend = 0.00
        # if categories need to be filtetered, they are filtered and then their total expediture is calculated
        if pastMonthsFilterApplied:
            filteredCategories = category.expenditures.filter(date__gte=pastMonthsFilterApplied)
            for expense in filteredCategories:
                categorySpend += float(expense.amount)
        else:
            # in the case that no filter is applied (the first main graph us being generated), the labels are loaded
            names.append(category.name)

        if timePeriod == 'day':
            budgetCalculated = convertBudgetToDaily(category)
            if pastMonthsFilterApplied:
                # for the filtered smaller graphs, the average spending per day is calculated
                days = numberOfDaysWeeksMonthsArray[0]
                categorySpend = categorySpend/days
            else:
                # for the larger main graph, we filter for the most recent day's expeditures
                yesterday = today - timedelta(days=1)
                filteredCategories = category.expenditures.filter(date__gte=yesterday)

        if timePeriod == 'week':
            budgetCalculated = convertBudgetToWeekly(category)
            if pastMonthsFilterApplied:
                # for the filtered smaller graphs, the average spending per week is calculated
                weeks = numberOfDaysWeeksMonthsArray[1]
                categorySpend = categorySpend/weeks
            else:
                # for the larger main graph, we filter for the most recent week's expeditures
                weekStart = today
                weekStart -= timedelta(days=weekStart.weekday())
                weekEnd = today + timedelta(days = 1)
                filteredCategories = category.expenditures.filter(date__gte=weekStart, date__lt=weekEnd)

        if timePeriod == 'month':
            budgetCalculated = convertBudgetToMonthly(category)
            if pastMonthsFilterApplied:
                # for the filtered smaller graphs, the average spending per month is calculated
                months = numberOfDaysWeeksMonthsArray[2]
                categorySpend = categorySpend/months
            else:
                # for the larger main graph, we filter for the most recent month's expeditures
                filteredCategories = category.expenditures.filter(date__month=today.month, date__year=today.year)

        if pastMonthsFilterApplied==None:
            # for the main graph, all expeditures are added up for each category
            for expense in filteredCategories:
                categorySpend += float(expense.amount)

        # capping the maximum data to 100%
        amount = categorySpend/float(budgetCalculated)*100
        if amount < 100:
            data.append(round(amount,2))
        else:
            data.append(100)

    if pastMonthsFilterApplied:
        # the smaller graphs are reusing labels from the bigger graph generated first so only data is neede for them
        return data
    else:
        # the main graph needs both labels and data to be returned for its use
        returnedArrays = []
        returnedArrays.append(names)
        returnedArrays.append(data)
        return returnedArrays
