'''Helper file for points functionality.'''
from walletwizard.models import Points, Category
from .notificationsHelpers import createBasicNotification
from decimal import Decimal

'''
Updates the user's point based on the amount given as an argument.
If amount is negative the user loses points otherwise they gain points.
'''
def updateUserPoints(user, amount):
    points = Points.objects.get(user=user)
    if points.count + amount < 0:
        points.count = 0
    else:
        points.count += amount
    points.save()
    updateHousePoints(user, amount)

def createUserPoints(requestUser):
    points = Points.objects.create(user=requestUser, count=50)
    points.save()
    return points.count

def updateHousePoints(user, amount):
    house = user.house
    house.points += amount
    house.save()
    
    title = ''
    message = ''
    if amount < 0:
        amount = amount * -1
        title = "House points lost!"
        message = str(house.name) + " has lost " + str(amount) + " points"
    else:
        title = "House points gained!"
        message = str(house.name) + " has gained " + str(amount) + " points"
    
    createBasicNotification(user, title, message)

'''
Handles user losing points based on the percentage they've gone over their spending limit.
Only called if over the limit.
'''
loseUserPointsData = [
    [0, 10, -3, "Points Lost!",  "3 points lost for going over target"],
    [10, 30, -5, "Points Lost!",  "5 points lost for going over target"],
    [30, 50, -10, "Points Lost!",  "10 points lost for going over target"],
    [50, 70, -15, "Points Lost!",  "15 points lost for going over target"],
    [70, 100, -20, "Points Lost!",  "20 points lost for going over target"],
    [100, float('inf'), -25, "Points Lost!",  "25 points lost for going over target"],
]

def loseUserPoints(user, limit, spent):
    if limit == 0:
        return
    percentage = 100 * (spent - limit)/limit
    for data in loseUserPointsData: 
        if (percentage > data[0] and percentage <= data[1]):
            updateUserPoints(user, data[2])
            createBasicNotification(user, data[3], data[4])
            return
        
'''
Checks if the category is over its set spending limit.
Returns True if over, else returns False.
'''
def isCategoryOverSpendingLimit(category):
    return category.spendingLimit.amount < category.totalSpent()

'''
Handles the user gaining and losing points after an expenditure is made.
User gains 5 points for staying within limit, and gets a warning notifications if they have used 85% 
or more of their spending Limit.
User loses points if they are over the limit. 
'''
def updateUserPointsForExpenditureCreation(user, category, overLimit):
    expenditure = category.expenditures.latest('createdAt')
    
    spendingCurrent = category.totalSpent()
    spendingLimit = category.spendingLimit.amount
    
    if overLimit:
        # if category was already over limit, lose point depending on new expenditure not previous overdraft(s)
        loseUserPoints(user, spendingLimit, spendingLimit + expenditure.amount)
    else:
        if spendingCurrent > spendingLimit:
            loseUserPoints(user, spendingLimit, spendingCurrent)
        else:
            closeAmount = spendingLimit * Decimal(0.85)
            if spendingCurrent >= closeAmount:
                createBasicNotification(user, "Watch out!", "You are nearing your spending limit for " + category.name)
            updateUserPoints(user, 5)
            createBasicNotification(user, "Points Won!", "5 points for staying within target for " + category.name)