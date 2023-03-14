from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from libgravatar import Gravatar
from .helpers.modelUtils import computeTotalSpent
from datetime import datetime
from django.utils import timezone
from decimal import Decimal

class SpendingLimit(models.Model):
    '''model for setting and monitoring user's financial goals and spending limits.'''

    TIME_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ]
    timePeriod = models.CharField(max_length=20, choices=TIME_CHOICES, blank=True)
    amount = models.DecimalField(max_digits=10, validators=[MinValueValidator(0.01)], decimal_places=2)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-createdAt']

    def __str__(self):
        return f'£{self.amount}, {self.timePeriod}'

    def getNumber(self):
        return self.amount


class Expenditure(models.Model):
    '''model for storing and tracking user expenditures.'''
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, validators=[MinValueValidator(0.01)], decimal_places=2)
    date = models.DateField()
    receipt = models.ImageField(upload_to='receipts/', blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

class Category(models.Model):
    '''model for storing and managing user expense categories.'''

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='users')
    name = models.CharField(max_length=80)
    spendingLimit = models.ForeignKey(SpendingLimit, on_delete=models.CASCADE, blank=True)
    expenditures = models.ManyToManyField(Expenditure, related_name='expenditures')
    description = models.TextField(blank=True)
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

    def __str__(self):
        return self.name
            
class User(AbstractUser):
    '''model for user authentication.'''

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

    class Meta:
        ordering = ['username']

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def miniGravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    def fullName(self):
        return f'{self.firstName} {self.lastName}'

    def isFollowing(self, user):
        """Returns whether self follows the given user."""

        return user in self.followees.all()

    def followerCount(self):
        """Returns the number of followers of self."""

        return self.followers.count()

    def followeeCount(self):
        """Returns the number of followees of self."""

        return self.followees.count()

    def getHouse(self):
        houses = ['RED', 'BLUE', 'YELLOW', 'GREEN']

        return houses[self.id % len(houses)]

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


class Notification(models.Model):
    '''model for storing and managing user notifications.'''

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


class Points(models.Model):
    ''' model for the points that the user earns '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pointsNum = models.IntegerField(default=0)
    
