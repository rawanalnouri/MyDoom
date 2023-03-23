from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from libgravatar import Gravatar
from .helpers.modelHelpers import computeTotalSpendingLimitByMonth, computeTotalSpentInTimePeriod
from datetime import datetime
from django.utils import timezone
from decimal import Decimal

class SpendingLimit(models.Model):
    '''Model for storing and managing user's spending limits for each category and overall.'''
    TIME_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ]
    timePeriod = models.CharField(max_length=20, choices=TIME_CHOICES, blank=False)
    amount = models.DecimalField(max_digits=20, validators=[MinValueValidator(0.01)], decimal_places=2)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        '''Model options.'''

        ordering = ['-createdAt']

    def __str__(self):
        return f'£{self.amount}, {self.timePeriod}'

    def getNumber(self):
        return self.amount

class Expenditure(models.Model):
    '''Model for storing and managing user expenditures.'''
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=250, blank=True)
    amount = models.DecimalField(max_digits=10, validators=[MinValueValidator(0.01)], decimal_places=2)
    date = models.DateField()
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        '''Model options.'''

        ordering = ['-date']

    def __str__(self):
        return self.title

class Category(models.Model):
    '''Model for storing and managing categories that users will add expenditures to.'''
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='users')
    name = models.CharField(max_length=50)
    spendingLimit = models.ForeignKey(SpendingLimit, on_delete=models.CASCADE)
    expenditures = models.ManyToManyField(Expenditure, related_name='expenditures', blank=True)
    description = models.CharField(blank=True, max_length=250)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def progressAsPercentage(self):
        total = computeTotalSpentInTimePeriod(self.spendingLimit.timePeriod, self.expenditures)
        if self.spendingLimit.amount==0:
            return 0.00
        else:
            return round(100*total/float(self.spendingLimit.amount), 2)
    
    def totalSpentInTimePeriod(self):
        return Decimal(round(computeTotalSpentInTimePeriod(self.spendingLimit.timePeriod, self.expenditures), 2))

    def totalSpendingLimitByMonth(self):
        return Decimal(round(computeTotalSpendingLimitByMonth(self.spendingLimit.timePeriod, self.spendingLimit.amount), 2))

    def __str__(self):
        return self.name

class House(models.Model):
    '''Model for storing and managing houses.'''
    points = models.IntegerField(default=0)
    name = models.CharField(max_length=50, unique=True, blank=False)
    memberCount = models.IntegerField(default=0, validators=[MinValueValidator(0)])

class User(AbstractUser):
    '''Model for storing and managing users.'''
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
        '''Model options.'''

        ordering = ['username']

    def fullName(self):
        return f'{self.firstName} {self.lastName}'
    
    def gravatar(self, size=120):
        '''Return a URL to the user's gravatar'''
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def miniGravatar(self):
        '''Return a URL to a miniature version of the user's gravatar.'''
        return self.gravatar(size=60)

    def isFollowing(self, user):
        '''Returns whether self follows the given user.'''
        return user in self.followees.all()

    def followerCount(self):
        '''Return the number of followers of self.'''
        return self.followers.count()

    def followeeCount(self):
        '''Return the number of followees of self.'''
        return self.followees.count()

    def progressAsPercentage(self):
        '''Return the user's total category progress as a percentage.'''
        limit = 0.0
        total = 0.0
        for category in self.categories.all():
            limit += float(category.spendingLimit.amount)
            total += computeTotalSpentInTimePeriod(category.spendingLimit.timePeriod, category.expenditures)
        if limit == 0:
            return 0.00
        else:
            return round(100 * total/limit, 2)
    
    def totalSpentThisMonth(self):
        '''Return the total amount spent by the user this month.'''
        total = 0.0
        today = datetime.now()
        for category in self.categories.all():
            for expense in category.expenditures.filter(date__month=today.month):
                total += float(expense.amount)
        return round(total, 2)

class Notification(models.Model):
    '''Model for storing and managing user notifications.'''
    toUser = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=80, blank=False)
    message = models.CharField(max_length=250, blank=False)
    isSeen = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('category', 'Category'),
        ('follow', 'Follow')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=False)

    class Meta:
        '''Model options.'''

        ordering = ['-createdAt']

    def __str__(self):
        return self.message
    
class ShareCategoryNotification(Notification):
    '''Model for storing and managing share category notifications.'''
    sharedCategory = models.ForeignKey(Category, on_delete=models.CASCADE)
    fromUser = models.ForeignKey(User, on_delete=models.CASCADE)

class FollowRequestNotification(Notification):
    '''Model for storing and managing follow request notifications.'''
    fromUser = models.ForeignKey(User, on_delete=models.CASCADE)

class Points(models.Model):
    '''Model for storing and managing user points.'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        '''Model options.'''

        ordering = ['-count']