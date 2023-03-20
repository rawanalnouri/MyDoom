from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import User, Category, SpendingLimit, Expenditure
from django.core.validators import RegexValidator
from ExpenseTracker.helpers.notificationsHelpers import *
from ExpenseTracker.helpers.modelHelpers import *
import os
from decimal import Decimal

class SignUpForm(forms.ModelForm):
    '''Form to allow a user to sign up to the system'''

    class Meta:
        model = User
        fields = ["firstName", "lastName", "username", "email"]

    firstName = forms.CharField(label="First name")
    lastName = forms.CharField(label="Last name")
    newPassword = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$', #using postive lookaheads
            message="Password must contain an uppercase character, lowercase character and a number!"
        )]
    )
    passwordConfirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        newPassword = self.cleaned_data.get("newPassword")
        passwordConfirmation = self.cleaned_data.get("passwordConfirmation")
        if newPassword != passwordConfirmation:
            self.add_error("passwordConfirmation", "Confirmation does not match password.")

    '''Creates a new user and saves it to the database'''
    def save(self):
        super().save(commit=False)
        newUser = User.objects.create_user(
            username=self.cleaned_data.get('username').lower(),
            firstName=self.cleaned_data.get('firstName'),
            lastName=self.cleaned_data.get('lastName'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('newPassword'),
        )
        return newUser


'''Form to allow a user to login'''
class LogInForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class ExpenditureForm(forms.ModelForm):
    otherCategory = forms.ChoiceField(label = "Select category to share expenditure with",)

    class Meta:
        model = Expenditure
        fields = ['title', 'description', 'amount', 'date','receipt']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user, category, *args, **kwargs):
        self.user = user
        self.category = category
        super(ExpenditureForm, self).__init__(*args, **kwargs)
        self.initialReceipt = None
        if kwargs:
            self.initialReceipt = kwargs["instance"].receipt
        self.fields['otherCategory'].choices = self.getCategoryChoices()

        
    def getCategoryChoices(self):
        categoryArray = [(-1, "None")]
        for x in Category.objects.filter(users__in=[self.user]).exclude(id=self.category.id):
            categoryArray.append((x.id, x))
        return categoryArray

        
    def save(self, commit=True):
        expenditure = super().save()
        if commit:
            self.category.expenditures.add(expenditure)
            self.category.save()

            # Handling extra categories
            otherCategoryId = self.cleaned_data.get("otherCategory")
                
            if (int(otherCategoryId) >= 0):
                otherCategory = Category.objects.get(id = int(otherCategoryId))
                otherCategory.expenditures.add(expenditure)
                otherCategory.save()

            # Removing old file from media folder
            newReceipt = self.cleaned_data.get("receipt")
            if (self.initialReceipt != None and self.initialReceipt != newReceipt):
                path = os.path.join(settings.MEDIA_ROOT, self.initialReceipt.name)
                if not os.path.isdir(path):
                    os.remove(path)

            expenditure.save() 
        return expenditure


class CategorySpendingLimitForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description']
        widgets = {
            'spendingLimit': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CategorySpendingLimitForm, self).__init__(*args, **kwargs)

    timePeriod = forms.ChoiceField(label="Time period", choices=SpendingLimit.TIME_CHOICES)
    amount = forms.DecimalField(label="Amount [GBP]", min_value=0.01)

    def save(self, commit=True):
        category = super().save(commit=False)
        spendingLimit = SpendingLimit.objects.create(
            timePeriod=self.cleaned_data['timePeriod'],
            amount=self.cleaned_data['amount']
        )
        category.spendingLimit = spendingLimit
        if commit:
            spendingLimit.save()
            category.save()
            category.users.add(self.user)
            self.user.categories.add(category)
        return category

    def validateName(self, name):
        existingCategories = Category.objects.filter(
            name__iexact=name, users__in=[self.user]
        ).exclude(id=self.instance.id)

        if existingCategories.exists():
            raise forms.ValidationError(
                'Category with this name already exists for this user.', code='invalid'
            )
    
    def validateSpendingLimits(self, timePeriod, amount):
        categoriesTotal = Decimal(0)
        for category in Category.objects.all():
            categoriesTotal += category.totalSpendingLimitByMonth()

        categoriesTotal += computeTotalSpendingLimitByMonth(timePeriod, amount)
        overallTimePeriod = self.user.overallSpendingLimit.timePeriod
        overallAmount = self.user.overallSpendingLimit.amount
        overallTotal = computeTotalSpendingLimitByMonth(
            overallTimePeriod, overallAmount
        )

        if categoriesTotal > overallTotal:
            raise forms.ValidationError(
                'The amount you\'ve chosen for this category\'s spending limit is too high'
                ' compared to your overall spending limit.', code='invalid'
            )

    def clean(self):
        cleanedData = super().clean()
        amount = cleanedData.get('amount')
        if amount:
            timePeriod = cleanedData.get('timePeriod')
            amount = Decimal(amount)
            if (self.user.overallSpendingLimit):
                self.validateSpendingLimits(timePeriod, amount)
        name = cleanedData.get('name')
        self.validateName(name)
        return cleanedData


class EditProfile(forms.ModelForm):
    firstName = forms.CharField(label='First name')
    lastName = forms.CharField(label='Last name')

    class Meta:
        model = User
        fields = ["firstName", "lastName", "username", "email"]


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Old Password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'New Password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        })


class ShareCategoryForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.none())

    class Meta:
        model = Category
        fields = []

    def __init__(self, fromUser, category, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = fromUser.followers.all()
        self.category = category
        self.fromUser = fromUser

    # Sends a share request to the user selected
    def save(self, commit=True):
        toUser = self.cleaned_data['user']
        title = "New Category Shared!"
        message = self.fromUser.username + " wants to share a category '"+ self.category.name +"' with you"
        createShareCategoryNotification(toUser, title, message, self.category, self.fromUser)
        return toUser
    
    def clean(self):
        cleanedData = super().clean()
        name = self.category.name
        toUser = cleanedData.get('user')
        if toUser is not None:
            existingCategory = toUser.categories.filter(name__iexact=name)
            if existingCategory.exists():
                raise forms.ValidationError('The user you want to share this category with already has a category with the same name.\n'
                                            + 'Change the name of the category before sharing.', code='invalid')
        return cleanedData


TIME_PERIOD_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]

'''Form to allow a user to select a category to generate a report for'''
class ReportForm(forms.Form):
    timePeriod = forms.ChoiceField(choices = TIME_PERIOD_CHOICES, label = "Time Frame")
    selectedCategory = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label = "Categories")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['selectedCategory'].choices = self.createCategorySelection()

    def createCategorySelection(self):
        categoryArray = []
        for x in Category.objects.filter(users__in=[self.user]):
            categoryArray.append((x.id, x))
        return categoryArray

class OverallSpendingForm(forms.Form):
    timePeriod = forms.ChoiceField(label="Time period", choices=SpendingLimit.TIME_CHOICES)
    amount = forms.DecimalField(label="Amount [GBP]", min_value=0.01)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(OverallSpendingForm, self).__init__(*args, **kwargs)

    def save(self):
        timePeriod = self.cleaned_data['timePeriod']
        amount = self.cleaned_data['amount']
        if self.user.overallSpendingLimit:
            currentLimit = self.user.overallSpendingLimit
            currentLimit.timePeriod = timePeriod
            currentLimit.amount = amount
            currentLimit.save()
        else:
            newLimit = SpendingLimit.objects.create(
                timePeriod=timePeriod,
                amount=amount
            )
            newLimit.save()
            self.user.overallSpendingLimit = newLimit
        self.user.save()
        return self.user.overallSpendingLimit
    
    def validateSpendingLimits(self, timePeriod, amount):
        categoriesTotal = Decimal(0)
        for category in Category.objects.all():
            categoriesTotal += category.totalSpendingLimitByMonth()

        amount = Decimal(amount)
        overallTotal = computeTotalSpendingLimitByMonth(timePeriod, amount)

        if categoriesTotal > overallTotal:
            raise forms.ValidationError('Your overall spending limit is too low compared to the spending '
                                    +'limits set in your categories.', code='invalid')

    def clean(self):
        cleanedData = super().clean()
        amount = cleanedData.get('amount')
        timePeriod = cleanedData.get('timePeriod')
        if amount:
            self.validateSpendingLimits(timePeriod, amount)
        return cleanedData