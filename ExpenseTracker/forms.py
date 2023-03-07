from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import User, Category, SpendingLimit, Expenditure
from django.core.validators import RegexValidator


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
    class Meta:
        model = Expenditure
        fields = ['title', 'description', 'amount', 'date', 'receipt', 'mood']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def save(self, category, commit=True):
        expenditure = super().save()
        if commit:
            category.expenditures.add(expenditure)
            category.save()
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
        spendingLimit = SpendingLimit.objects.create(timePeriod=self.cleaned_data['timePeriod'],
                                                     amount=self.cleaned_data['amount'])
        category.spendingLimit = spendingLimit
        if commit:
            spendingLimit.save()
            category.save()
            category.users.add(self.user)
            self.user.categories.add(category)
        return category


class EditProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ["firstName", "lastName", "username", "email"]


class ChangePasswordForm(PasswordChangeForm):

    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','type':'password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','type':'password'}))
    new_password2= forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','type':'password'}))

    class Meta:
        model = User
        fields=["old_password","new_password1","new_password2"]


class ShareCategoryForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.none())

    class Meta:
        model = Category
        fields = []

    def __init__(self, user, category, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = user.followers.all()
        self.category = category

    def save(self, commit=True):
        category = self.category
        user = self.cleaned_data['user']
        category.users.add(user)
        user.categories.add(category)
        if commit:
            category.save()
            user.save()
        return category

FAVORITE_COLORS_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]

'''Form to allow a user to select a category to generate a report for'''


# class CustomModelMultipleChoiceField(forms.ModelMultipleChoiceField):
#     def label_from_instance(self, member):
#         return "%s" % member.name
#
# class ReportForm(forms.Form):
#     # def __init__(self, *args, **kwargs):
#     #     self._pwd = kwargs.pop('pwd', None)
#     #     super().__init__(*args, **kwargs)
#
#     # def __init__(self, *args, **kwargs):
#     #     self.user = kwargs.pop('user')
#     #     super(ReportForm, self).__init__(*args, **kwargs)
#     #     self.fields['selectedCategory'].choices = self.createCategorySelection()
#
#     # def __init__(self, *args, **kwargs):
#     #     self._pwd = kwargs.pop('pwd', None)
#     #     super().__init__(*args, **kwargs)
#     #     password1 = self._pwd
#     # def __init__(self, *args, **kwargs):
#     #     """ Grants access to the request object so that only members of the current user
#     #     are given as options"""
#     #
#     #     self.request = kwargs.pop('request')
#     #     super(CreateMealForm, self).__init__(*args, **kwargs)
#     #     self.fields['selectedCategory'].queryset = Member.objects.filter(
#     #         user=self.request.user)
#
#     # def __init__(self, company_pk=None, *args, **kwargs):
#     #     super(AddUserForm, self).__init__(*args, **kwargs)
#     #     self.fields['user'].queryset = User.objects.filter(company__pk=company_pk)
#     #
#     # user = forms.ModelChoiceField(queryset=User.objects.all())
#
#     categoryArray = []
#     # for x in Category.objects.filter(users__in=[self.user]):
#     # for x in [1, 2, 3]:
#     for x in Category.objects.all():
#         categoryArray.append((x, x))
#
#     # def createCategorySelection(self):
#     #     categoryArray = []
#     #     # for x in Category.objects.filter(users__in=[self.user]):
#     #     # for x in [1, 2, 3]:
#     #     # for x in password1:
#     #         categoryArray.append((x, x))
#
#     timePeriod = forms.ChoiceField(choices = FAVORITE_COLORS_CHOICES, label = "Time Frame")
#     selectedCategory = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices = categoryArray, label = "Categories")
#
#     def userInput(self):
#         time = self.cleaned_data.get('timePeriod')
#         categories = self.cleaned_data.get('selectedCategory')
#         password1 = self._pwd # access your password from view
#
#     # selectedCategory = CustomModelMultipleChoiceField(
#     #     queryset=None,
#     #     widget=forms.CheckboxSelectMultiple
#     # )
#     # selectedCategory = forms.ModelMultipleChoiceField(
#     #     queryset=Category.objects.all(),
#     #     widget=forms.CheckboxSelectMultiple
#     # )
#
#     # def __init__(self, *args, **kwargs):
#     #     self.user = kwargs.pop('user')
#     #     super(ReportForm, self).__init__(*args, **kwargs)
#     #     self.fields['selectedCategory'].choices = self.createCategorySelection()

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
