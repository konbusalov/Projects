from django import forms
from .models import User, Account
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields = ['username','full_name','email','passport','passport_id','phone','password1','password2', 'role'] 

class AccountForm(forms.Form):
    class Meta:
        model=Account
        