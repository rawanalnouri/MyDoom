''' Helper file handling points functionality '''

from walletwizard.models import Points, Category
from .notificationsHelpers import createBasicNotification
from decimal import Decimal

'''
Updates the user's point based on the amount given as an argument.
If amount is negative the user loses points otherwise they gain points.
'''
def updatePoints(requestUser, amount):
    points = Points.objects.get(user=requestUser)
    if points.count + amount < 0:
        points.count = 0
    else:
        points.count = points.count + amount
    points.save()
    housePointsUpdate(requestUser, amount)

# Create the points for a user when they sign up
def createPoints(requestUser):
    points = Points.objects.create(user=requestUser, count=50)
    points.save()
    return points.count

# Updates the user's house points whenever they gain or lost points
def housePointsUpdate(user, amount):
    currentHouse = user.house
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
    
    createBasicNotification(user, title, message)

'''
Handles user losing points based on the percentage they've gone above their spending limit.
Only called if over the limit.
'''
losePointsData = [
 [0, 10, -3, "Points Lost!",  "3 points lost for going over target"],
 [10, 30, -5, "Points Lost!",  "5 points lost for going over target"],
 [30, 50, -10, "Points Lost!",  "10 points lost for going over target"],
 [50, 70, -15, "Points Lost!",  "15 points lost for going over target"],
 [70, 100, -20, "Points Lost!",  "20 points lost for going over target"],
 [100, float('inf'), -25, "Points Lost!",  "25 points lost for going over target"],
 ]

def losePoints(user, limit, spent):
    spentProportion = (spent-limit)/limit 
    percentage = spentProportion * 100
    for data in losePointsData: 
        if (percentage > data[0] and percentage <= data[1]):
            updatePoints(user, data[2])
            createBasicNotification(user, data[3], data[4])
            return
        
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
        return (True, totalSpent)

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
        # if they are already over the amount want to lose point depending on the new expenditure, not the previos overdraft 
        losePoints(user, Decimal(currentCategory.spendingLimit.amount), currentCategory.spendingLimit.amount + newExpenditureAmount)
