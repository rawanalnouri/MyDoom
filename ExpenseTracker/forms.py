from django import forms
from .models import User
from django.core.validators import RegexValidator

'''Form to allow a user to sign up to the system'''
class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]

    new_password = forms.CharField(
        label='New Password', 
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$', #using postive lookaheads
            message="Password must contain an uppeercase charachter, lowercase charachter and a number!"
        )]

    )
    password_confirmation = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput())


    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get("new_password") 
        password_confirmation = self.cleaned_data.get("password_confirmation")
        if new_password != password_confirmation:
            self.add_error("password_confirmation", "Confirmation does not match password.")

    '''Creates a new user and saves it to the database'''
    def save(self):
        super().save(commit=False)
        new_user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return new_user

'''Form to allow a user to login'''
class LogInForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

