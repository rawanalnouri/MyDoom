"""Configuration of the administrative interface for ExpenseTracker."""
from django.contrib import admin
from .models import User, Category, Expenditure, SpendingLimit, Notification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'id', 'username', 'firstName', 'lastName', 'email', 'is_active']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for categories."""

    list_display = [
        'id', 'name', 'description', 'spendingLimit',
    ]

@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for expenditures."""

    list_display = [
        'title', 'amount', 'description',
    ]

@admin.register(SpendingLimit)
class SpendingLimitAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for spending limits."""

    list_display = [
        'amount', 'timePeriod',
    ]

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for notifications."""

    list_display = [
        'toUser', 'message', 'isSeen', 'title',
    ]