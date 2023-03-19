from datetime import datetime
from datetime import timedelta
from decimal import Decimal

AVERAGE_DAYS_PER_MONTH = Decimal(30.4)
AVERAGE_WEEKS_PER_MONTH = Decimal(4.4)

# Function to compute spending in expenditures based on time period 
def computeTotalSpent(timePeriod, expenditures):
    total = 0.0
    today = datetime.now()
    if timePeriod == 'daily':
        for expense in expenditures.filter(date__day=today.day):
            total += float(expense.amount)
    elif timePeriod == 'weekly':
        startOfWeek = today - timedelta(days=today.weekday())
        for expense in expenditures.filter(date__gte=startOfWeek):
            total += float(expense.amount)
    elif timePeriod == 'monthly':
        for expense in expenditures.filter(date__month=today.month):
            total += float(expense.amount)
    elif timePeriod == 'yearly':
        for expense in expenditures.filter(date__year=today.year):
            total += float(expense.amount)
    return total

def computeTotalSpendingLimitByMonth(timePeriod, amount):
    result = 0.0
    if timePeriod == 'daily':
        result = Decimal(amount * AVERAGE_DAYS_PER_MONTH)
    elif timePeriod == 'weekly':
        result = Decimal(amount * AVERAGE_WEEKS_PER_MONTH)
    elif timePeriod == 'monthly':
        result = Decimal(amount)
    elif timePeriod == 'yearly':
        result = Decimal(amount / 12)
    return result