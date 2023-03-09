
from ExpenseTracker.models import Points, Category, SpendingLimit, Expenditure
from django.utils.timezone import datetime, timedelta
from .utils import createBasicNotification
from decimal import Decimal
#from
def addPoints(request,n):
    user = request.user
    pointsObject = Points.objects.get(user=request.user)
    # currentPoints = pointsObject.pointsNum
    points = Points.objects.get(user=request.user).pointsNum
    if points+n<0:
        pointsObject.pointsNum=0
    else:
        pointsObject.pointsNum = points+n
    pointsObject.save()



def losePoints(request,limit,spent):
    # call add points with a -ve
    # pass in spent and limit find percentage 
    #this function only called if we are over the limit 
    user = request.user
    spentProportion = (spent-limit)/limit 
    percentage = spentProportion*100
    if percentage<=10:
        addPoints(request,-3)
        createBasicNotification(request.user,"Points Lost!","3 points lost for going over target")
        print(spent)
    elif percentage>10 and percentage<=30:
        addPoints(request,-5)
        createBasicNotification(request.user,"Points Lost!","5 points lost for going over target")
    elif percentage>30 and percentage<=50:
        addPoints(request,-10)
        createBasicNotification(request.user,"Points Lost!","10 points lost for going over target")
    elif percentage>50 and percentage<=70:
        addPoints(request,-15)
        createBasicNotification(request.user,"Points Lost!","15 points lost for going over target")
    elif percentage>70 and percentage<=100:
        addPoints(request,-20)
        createBasicNotification(request.user,"Points Lost!","20 points lost for going over target")
    else:
        addPoints(request,-25)
        createBasicNotification(request.user,"Points Lost!","25 points lost for going over target")



def getTimePeriod(request,category):
    user = request.user
    # need a list of all categories and then do a for loop through them all 
   
    currentSpendingLimit = Category.objects.get(id=category.id).spendingLimit
    period = currentSpendingLimit.timePeriod
    return period



def checkIfOver(request,category):
    #get latest expenditure check how over they were before
    time=getTimePeriod(request,category)
    currentCategory = Category.objects.get(id=category.id)
    date = datetime.now()
    spent=0.00
    if time=='daily':
        for expence in currentCategory.expenditures.filter(date=datetime.now().date()):
            spent+=float(expence.amount)
        if abs(currentCategory.spendingLimit.amount) >= abs(spent): 
            return (False, spent)
        else:
            return(True, spent)
        
    elif time=='weekly':
        startOfWeek = date - timedelta(days=date.weekday())
        for expence in currentCategory.expenditures.filter(date__gte=startOfWeek):
            spent+=float(expence.amount)
        if abs(currentCategory.spendingLimit.amount) >= abs(spent): 
           return (False, spent)
        else:
            return(True, spent)
          
    elif time=='monthly':
         for expence in currentCategory.expenditures.filter(month__gte=date.month):
            spent+=float(expence.amount)
         if abs(currentCategory.spendingLimit.amount) >= abs(spent): 
           return (False, spent)
         else:
            return(True, spent)
    


def trackPoints(request,category,isOver,totalSpent):
    
    currentCategory = Category.objects.get(id=category.id)
    newExpenditure=currentCategory.expenditures.latest('createdAt')
    newExpenditureAmount = newExpenditure.amount
    newAmount = newExpenditureAmount+Decimal(totalSpent)
    if isOver==False:
       
        if newAmount>currentCategory.spendingLimit.amount:
            losePoints(request,currentCategory.spendingLimit.amount,newAmount)
            
        else:
            closeAmount = currentCategory.spendingLimit.amount * Decimal(0.85)
            if newAmount>=closeAmount:
                createBasicNotification(request.user,"Watch out","you are nearing your spending limit")
            addPoints(request,5)
            createBasicNotification(request.user,"Points Won!","5 points for staying within target :)")
        
    else:
        #if they are already over the amount want to loose point depending on the new expenditure, not the previos overdraft 
        losePoints(request,Decimal(currentCategory.spendingLimit.amount),currentCategory.spendingLimit.amount+newExpenditureAmount)

        










    
 

    





























