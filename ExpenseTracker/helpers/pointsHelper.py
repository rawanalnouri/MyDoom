from ExpenseTracker.models import Points, Category, SpendingLimit, Expenditure
from django.utils.timezone import datetime, timedelta
from .utils import createBasicNotification
from decimal import Decimal

"""
Updates the user's point based on the amount given as an argument.
If amount is negative the user loses points otherwise they gain points.
"""


def updatePoints(request, amount):
    pointsObject = Points.objects.get(user=request.user)
    points = Points.objects.get(user=request.user).pointsNum
    if points + amount < 0:
        pointsObject.pointsNum = 0
    else:
        pointsObject.pointsNum = points + amount
    pointsObject.save()
    housePointsUpdate(request, amount)


def housePointsUpdate(request, amount):
    currentHouse = request.user.house
    housePoints = currentHouse.points
    currentHouse.points = housePoints + amount
    currentHouse.save()
    
    title = ''
    message = ''
    if amount < 0:
        amount = amount * -1
        title = "House points lost!"
        message = str(currentHouse.name) + " has lost " + str(amount) + " points"
    else:
        title = "House points gained!"
        message = str(currentHouse.name) + " has gained " + str(amount) + " points"
    
    createBasicNotification(request.user, title, message )

   

    
    

   


"""
Handles user losing points based on the percentage they've gone above their spending limit.
Only called if over the limit
"""


def losePoints(request, limit, spent):
    spentProportion = (spent - limit) / limit
    percentage = spentProportion * 100
    if percentage <= 10:
        updatePoints(request, -3)
        createBasicNotification(request.user, "Points Lost!", "3 points lost for going over target")
    elif percentage > 10 and percentage <= 30:
        updatePoints(request, -5)
        createBasicNotification(request.user, "Points Lost!", "5 points lost for going over target")
    elif percentage > 30 and percentage <= 50:
        updatePoints(request, -10)
        createBasicNotification(request.user, "Points Lost!", "10 points lost for going over target")
    elif percentage > 50 and percentage <= 70:
        updatePoints(request, -15)
        createBasicNotification(request.user, "Points Lost!", "15 points lost for going over target")
    elif percentage > 70 and percentage <= 100:
        updatePoints(request, -20)
        createBasicNotification(request.user, "Points Lost!", "20 points lost for going over target")
    else:
        updatePoints(request, -25)
        createBasicNotification(request.user, "Points Lost!", "25 points lost for going over target")


""" 
Checks if the user is already over their spending limit.
Returns boolean for if over over and the total amount the user has spent within their 
current spending limit.
"""


def checkIfOver(category):
    currentCategory = Category.objects.get(id=category.id)

    totalSpent = currentCategory.totalSpent()
    if abs(currentCategory.spendingLimit.amount) >= abs(totalSpent):
        return (False, totalSpent)
    else:
        return (True, totalSpent)


""" 
Handles the user gaining and losing points.
User gains 5 points for staying within limit, and get notifications if they have used 85% or more 
of their spending Limit.
User loses points if they are over the limit. 
"""


def trackPoints(request, category, isOver, totalSpent):
    currentCategory = Category.objects.get(id=category.id)
    newExpenditure = currentCategory.expenditures.latest("createdAt")
    newExpenditureAmount = newExpenditure.amount
    newAmount = newExpenditureAmount + Decimal(totalSpent)

    if isOver == False:
        if newAmount > currentCategory.spendingLimit.amount:
            losePoints(request, currentCategory.spendingLimit.amount, newAmount)

        else:
            closeAmount = currentCategory.spendingLimit.amount * Decimal(0.85)
            if newAmount >= closeAmount:
                createBasicNotification(request.user,"Watch out!","You are nearing your spending limit for " + currentCategory.name,)
            updatePoints(request, 5)
            createBasicNotification(request.user,"Points Won!","5 points for staying within target for " + currentCategory.name,)

    else:
        # if they are already over the amount want to loose point depending on the new expenditure, not the previos overdraft
        losePoints(request,Decimal(currentCategory.spendingLimit.amount),currentCategory.spendingLimit.amount + newExpenditureAmount)
