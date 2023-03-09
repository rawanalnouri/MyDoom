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
        return category.spendingLimit.getNumber()/54
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
