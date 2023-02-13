from django import forms
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

    timePeriod = forms.ChoiceField(choices=SpendingLimit.TIME_CHOICES)
    amount = forms.DecimalField(label="Amount [GBP]", min_value=0.01)

    def save(self, commit=True):
        category = super().save(commit=False)
        spendingLimit = SpendingLimit.objects.create(timePeriod=self.cleaned_data['timePeriod'],
                                                     amount=self.cleaned_data['amount'])
        category.spendingLimit = spendingLimit
        category.user = self.user
        if commit:
            spendingLimit.save()
            category.save()
            self.user.categories.add(category)
        return category

def createCategorySelection():
    categoryArray = []
    # filter for user!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for x in Category.objects.all():
        categoryArray.append((x, x))
    return categoryArray

FAVORITE_COLORS_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]

'''Form to allow a user to select a category to generate a report for'''
class ReportForm(forms.Form):
    timePeriod = forms.ChoiceField(choices = FAVORITE_COLORS_CHOICES, label = "Time Frame: ")
    selectedCategory = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=createCategorySelection())
