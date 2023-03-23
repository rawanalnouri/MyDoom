from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from libgravatar import Gravatar
from .helpers.modelHelpers import *
from datetime import datetime
from django.utils import timezone
from decimal import Decimal

'''model for setting and monitoring user's financial goals and spending limits.'''
class SpendingLimit(models.Model):

    TIME_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ]
    timePeriod = models.CharField(max_length=20, choices=TIME_CHOICES, blank=False)
    amount = models.DecimalField(max_digits=50, validators=[MinValueValidator(0.01)], decimal_places=2)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-createdAt']

    def __str__(self):
        return f'£{self.amount}, {self.timePeriod}'

    def getNumber(self):
        return self.amount

'''model for storing and tracking user expenditures.'''
class Expenditure(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, validators=[MinValueValidator(0.01)], decimal_places=2)
    date = models.DateField()
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

'''model for storing and managing user expense categories.'''
class Category(models.Model):

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='users')
    name = models.CharField(max_length=50)
    spendingLimit = models.ForeignKey(SpendingLimit, on_delete=models.CASCADE)
    expenditures = models.ManyToManyField(Expenditure, related_name='expenditures', blank=True)
    description = models.CharField(blank=True, max_length=250)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def progress(self):
        total = computeTotalSpent(self.spendingLimit.timePeriod, self.expenditures)
        if self.spendingLimit.amount==0:
            return 0.00
        else:
            return round(100*total/float(self.spendingLimit.amount), 2)
    
    def totalSpent(self):
        return Decimal(round(computeTotalSpent(self.spendingLimit.timePeriod, self.expenditures), 2))

    def totalSpendingLimitByMonth(self):
        return Decimal(round(computeTotalSpendingLimitByMonth(self.spendingLimit.timePeriod, self.spendingLimit.amount), 2))

    def __str__(self):
        return self.name

''' model for the different houses '''
class House(models.Model):
    # image= models.ImageField(upload_to='images/') 
    points = models.IntegerField(default=0)
    # HOUSE_CHOICES = {'one','two','three','four'}
    name = models.CharField(max_length=50, unique=True, blank=False)
    memberCount = models.IntegerField(default=0, validators=[MinValueValidator(0)])

'''model for user authentication.'''
class User(AbstractUser):
    username   = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\w{3,}$',
            message='Username must contain at least three alphanumericals.'
        )]
    )
    firstName = models.CharField(max_length=50)
    lastName  = models.CharField(max_length=50)
    email      = models.EmailField(unique=True, blank=False)
    categories = models.ManyToManyField(Category, related_name='categories')
    followers = models.ManyToManyField(
        'self', symmetrical=False, related_name='followees'
    )
    lastLogin = models.DateTimeField(default=timezone.now)
    house = models.ForeignKey(House, on_delete=models.CASCADE, blank=True, null=True)
    overallSpendingLimit = models.ForeignKey(SpendingLimit, on_delete=models.CASCADE, blank=True, null=True)
    

    class Meta:
        ordering = ['username']

    '''Return a URL to the user's gravatar'''
    def gravatar(self, size=120):
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    '''Return a URL to a miniature version of the user's gravatar.'''
    def miniGravatar(self):
        return self.gravatar(size=60)

    def fullName(self):
        return f'{self.firstName} {self.lastName}'

    '''Returns whether self follows the given user.'''
    def isFollowing(self, user):
        return user in self.followees.all()

    '''Returns the number of followers of self.'''
    def followerCount(self):
        return self.followers.count()

    '''Returns the number of followees of self.'''
    def followeeCount(self):
        return self.followees.count()

    def totalProgress(self):
        total = 0.0
        limit = 0.0
        for category in self.categories.all():
            limit += float(category.spendingLimit.amount)
            total += computeTotalSpent(category.spendingLimit.timePeriod, category.expenditures)
        if limit==0:
            return 0.00
        else:
            return round(100*total/limit, 2)
    
    def totalSpentThisMonth(self):
        total = 0.0
        today = datetime.now()
        for category in self.categories.all():
            for expense in category.expenditures.filter(date__month=today.month):
                total += float(expense.amount)
        return round(total, 2)

'''model for storing and managing user notifications.'''
class Notification(models.Model):

    toUser = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    isSeen = models.BooleanField(default = False)
    TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('category', 'Category'),
        ('follow', 'Follow')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=False)

    class Meta:
        ordering = ['-createdAt']

    def __str__(self):
        return self.message
    
class ShareCategoryNotification(Notification):
    sharedCategory = models.ForeignKey(Category, on_delete=models.CASCADE)
    fromUser = models.ForeignKey(User, on_delete=models.CASCADE)

class FollowRequestNotification(Notification):
    fromUser = models.ForeignKey(User, on_delete=models.CASCADE)

''' model for the points that the user earns '''
class Points(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-count']