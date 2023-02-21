from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from libgravatar import Gravatar

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



class Expenditure(models.Model):
    '''model for storing and tracking user expenditures.'''

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, validators=[MinValueValidator(0.01)], decimal_places=2)
    date = models.DateField()
    receipt = models.ImageField(upload_to='receipts/', blank=True)
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('content', 'Content'),
        ('indifferent', 'Indifferent'),
        ('anxious', 'Anxious')
    ]
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return self.title

class Category(models.Model):
    '''model for storing and managing user expense categories.'''

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    spendingLimit = models.ForeignKey(SpendingLimit, on_delete=models.CASCADE, blank=True)
    expenditures = models.ManyToManyField(Expenditure, related_name='expenditures')
    description = models.TextField(blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
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

    def toggleFollow(self, followee):
        """Toggles when self follows a different user."""

        if followee==self:
            return
        if self.isFollowing(followee):
            self._unfollow(followee)
        else:
            self._follow(followee)

    def _follow(self, user):
        user.followers.add(self)

    def _unfollow(self, user):
        user.followers.remove(self)

    def isFollowing(self, user):
        """Returns whether self follows the given user."""

        return user in self.followees.all()

    def followerCount(self):
        """Returns the number of followers of self."""

        return self.followers.count()

    def followeeCount(self):
        """Returns the number of followees of self."""

        return self.followees.count()


class Notification(models.Model):
    '''model for storing and managing user notifications.'''

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    isSeen = models.BooleanField(default = False)

    class Meta:
        ordering = ['-createdAt']
    
    def __str__(self):
        return self.message