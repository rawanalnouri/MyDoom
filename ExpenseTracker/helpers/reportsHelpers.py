from datetime import datetime
from datetime import timedelta
from ExpenseTracker.models import *

def convertBudgetToDaily(category):
    currentTimePeriod = category.spendingLimit.timePeriod
    if currentTimePeriod == 'weekly':
        return category.spendingLimit.getNumber()/7
    elif currentTimePeriod == 'monthly':
        return category.spendingLimit.getNumber()/30
    elif currentTimePeriod == 'yearly':
        return category.spendingLimit.getNumber()/365
    else:
        return category.spendingLimit.getNumber()

def convertBudgetToWeekly(category):
    currentTimePeriod = category.spendingLimit.timePeriod
    if currentTimePeriod == 'daily':
        return category.spendingLimit.getNumber()*7
    elif currentTimePeriod == 'monthly':
        return category.spendingLimit.getNumber()/4
    elif currentTimePeriod == 'yearly':
        return category.spendingLimit.getNumber()/52
    else:
        return category.spendingLimit.getNumber()

def convertBudgetToMonthly(category):
    currentTimePeriod = category.spendingLimit.timePeriod
    if currentTimePeriod == 'daily':
        return category.spendingLimit.getNumber()*30
    elif currentTimePeriod == 'monthly':
        return category.spendingLimit.getNumber()/4
    elif currentTimePeriod == 'yearly':
        return category.spendingLimit.getNumber()/54
    else:
        return category.spendingLimit.getNumber()

def createArraysData(categories, timePeriod, filter='', divisions=''):
    today = datetime.now()
    names = []
    data =[]
    filteredCategories=''
    for selected in categories:
        category = Category.objects.get(id=selected)
        if filter!='':
            filteredCategories = category.expenditures.filter(date__gte=filter)
        budgetCalculated = category.spendingLimit.getNumber()
        # total spend per catagory
        categorySpend = 0.00
        if filter!='':
            for expence in filteredCategories:
                categorySpend += float(expence.amount)
        else:
            names.append(category.name)

        if timePeriod == 'day':
            budgetCalculated = convertBudgetToDaily(category)
            if filter!='':
                categorySpend = categorySpend/divisions[0]
            else:
                yesterday = today - timedelta(days=1)
                filteredCategories = category.expenditures.filter(date__gte=yesterday)

        if timePeriod == 'week':
            budgetCalculated = convertBudgetToWeekly(category)
            if filter!='':
                categorySpend = categorySpend/divisions[1]
            else:
                week_start = today
                week_start -= timedelta(days=week_start.weekday())
                week_end = today + timedelta(days = 1)
                startOfWeek = today - timedelta(days=today.weekday())
                filteredCategories = category.expenditures.filter(date__gte=week_start, date__lt=week_end)

        if timePeriod == 'month':
            budgetCalculated = convertBudgetToMonthly(category)
            if filter!='':
                categorySpend = categorySpend/divisions[2]
            else:
                filteredCategories = category.expenditures.filter(date__month=today.month, date__year=today.year)

        if filter=='':
            for expence in filteredCategories:
                categorySpend += float(expence.amount)

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