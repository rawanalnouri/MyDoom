from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.validators import MinValueValidator
from django.db.models import Q, F
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

class User(AbstractUser):
    '''model for user authentication.'''

    # groups = models.ManyToManyField(Group, related_name='expensetracker_groups')
    # user_permissions = models.ManyToManyField(Permission, related_name='expensetracker_permissions')
    username   = models.CharField(
        max_length=30, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals.'
        )]
    )
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    email      = models.EmailField(unique=True, blank=False)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

class Expenditure(models.Model):
    '''model for storing and tracking user expenditures.'''

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, validators=[MinValueValidator(0.01)], decimal_places=2)
    date = models.DateField()
    receipt = models.ImageField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class SpendingLimit(models.Model):
    '''model for setting and monitoring user's financial goals and spending limits.'''

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(max_digits=10, validators=[MinValueValidator(0.01)], decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(start_date__lte=F('end_date')), name='date_start_before_end')
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Budget for {self.user.username}'

class Category(models.Model):
    '''model for storing and managing user expense categories.'''

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    expenditures = models.ManyToManyField(Expenditure, related_name='expenditures')
    spending_limit = models.ForeignKey(SpendingLimit, on_delete=models.CASCADE, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Notification(models.Model):
    '''model for storing and managing user notifications.'''

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.message