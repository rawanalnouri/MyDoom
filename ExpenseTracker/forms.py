from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import User, Category, SpendingLimit, Expenditure, Post
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

# Had to use snake case as I am referenceing variables that already exist


class PostForm(forms.ModelForm):
    """Form to ask user for post text.

    The post author must be by the post creator.
    """

    class Meta:
        """Form options."""

        model = Post
        fields = ['text']
        widgets = {
            'text': forms.Textarea()
        }