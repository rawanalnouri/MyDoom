
from ExpenseTracker.models import Points, Category, SpendingLimit, Expenditure
from django.utils.timezone import datetime, timedelta
from .utils import createBasicNotification
from decimal import Decimal

'''
Updates the user's point based on the amount given as an argument.
If amount is negative the user loses points otherwise they gain points.
'''
def updatePoints(user, amount):
    points = Points.objects.get(user=user)
    if points.pointsNum + amount < 0:
        points.pointsNum = 0
    else:
        points.pointsNum = points.pointsNum + amount
    points.save()

def createPoints(user):
    points = Points.objects.create(user=user, pointsNum=50)
    points.save()
    return points.pointsNum

'''
Handles user losing points based on the percentage they've gone above their spending limit.
Only called if over the limit
'''
def losePoints(user, limit, spent):
    spentProportion = (spent-limit)/limit 
    percentage = spentProportion*100
    if percentage <= 10:
        updatePoints(user, -3)
        createBasicNotification(user, "Points Lost!", "3 points lost for going over target")
    elif percentage > 10 and percentage <= 30:
        updatePoints(user,-5)
        createBasicNotification(user, "Points Lost!", "5 points lost for going over target")
    elif percentage>30 and percentage<=50:
        updatePoints(user, -10)
        createBasicNotification(user,"Points Lost!", "10 points lost for going over target")
    elif percentage>50 and percentage<=70:
        updatePoints(-15)
        createBasicNotification(user, "Points Lost!", "15 points lost for going over target")
    elif percentage>70 and percentage<=100:
        updatePoints(user, -20)
        createBasicNotification(user,"Points Lost!","20 points lost for going over target")
    else:
        updatePoints(user, -25)
        createBasicNotification(user, "Points Lost!", "25 points lost for going over target")


''' 
Checks if the user is already over their spending limit.
Returns boolean for if over over and the total amount the user has spent within their 
current spending limit.
'''
def checkIfOver(category):
    currentCategory = Category.objects.get(id=category.id)

    totalSpent = currentCategory.totalSpent()
    if abs(currentCategory.spendingLimit.amount) >= abs(totalSpent): 
        return (False, totalSpent)
    else:
        return(True, totalSpent)

    
''' 
Handles the user gaining and losing points.
User gains 5 points for staying within limit, and get notifications if they have used 85% or more 
of their spending Limit.
User loses points if they are over the limit. 
'''
def trackPoints(user, category, isOver, totalSpent):
    currentCategory = Category.objects.get(id=category.id)
    newExpenditure = currentCategory.expenditures.latest('createdAt')
    newExpenditureAmount = newExpenditure.amount
    newAmount = newExpenditureAmount + Decimal(totalSpent)

    if isOver==False:
        if newAmount > currentCategory.spendingLimit.amount:
            losePoints(user, currentCategory.spendingLimit.amount, newAmount)
            
        else:
            closeAmount = currentCategory.spendingLimit.amount * Decimal(0.85)
            if newAmount >= closeAmount:
                createBasicNotification(user, "Watch out!", "You are nearing your spending limit for " + currentCategory.name)
            updatePoints(user, 5)
            createBasicNotification(user, "Points Won!", "5 points for staying within target for " + currentCategory.name)

    else:
        #if they are already over the amount want to loose point depending on the new expenditure, not the previos overdraft 
        losePoints(user, Decimal(currentCategory.spendingLimit.amount), currentCategory.spendingLimit.amount + newExpenditureAmount)

        










    
 

    





























