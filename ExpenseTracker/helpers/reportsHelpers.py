''' Helper file containg method to generate data for graphs '''

from datetime import datetime
from datetime import timedelta
from ExpenseTracker.models import *

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

# Genrates data for the graphs on the reports page
def createArraysData(categories, timePeriod, filter='', divisions=''):
    today = datetime.now()
    names = []
    data =[]
    filteredCategories=''
    for selected in categories:
        category = Category.objects.get(id=selected)
        budgetCalculated = category.spendingLimit.getNumber()
        # total spend per catagory
    
        categorySpend = 0.00
        if filter != '':
            filteredCategories = category.expenditures.filter(date__gte=filter)
            for expense in filteredCategories:
                categorySpend += float(expense.amount)
        else:
            names.append(category.name)

        if timePeriod == 'day':
            budgetCalculated = convertBudgetToDaily(category)
            if filter != '':
                categorySpend = categorySpend/divisions[0]
            else:
                yesterday = today - timedelta(days=1)
                filteredCategories = category.expenditures.filter(date__gte=yesterday)

        if timePeriod == 'week':
            budgetCalculated = convertBudgetToWeekly(category)
            if filter!='':
                categorySpend = categorySpend/divisions[1]
            else:
                weekStart = today
                weekStart -= timedelta(days=weekStart.weekday())
                weekEnd = today + timedelta(days = 1)
                filteredCategories = category.expenditures.filter(date__gte=weekStart, date__lt=weekEnd)

        if timePeriod == 'month':
            budgetCalculated = convertBudgetToMonthly(category)
            if filter!='':
                categorySpend = categorySpend/divisions[2]
            else:
                filteredCategories = category.expenditures.filter(date__month=today.month, date__year=today.year)

        if filter=='':
            for expense in filteredCategories:
                categorySpend += float(expense.amount)

        amount = categorySpend/float(budgetCalculated)*100
        if amount < 100:
            data.append(round(amount,2))
        else:
            data.append(100)
    if filter!='':
        return data
    else:
        returnedArrays = []
        returnedArrays.append(names)
        returnedArrays.append(data)
        return returnedArrays