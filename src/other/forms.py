import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator


class UserCreationWithEmailForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if len(username) < 3 or len(username) > 16:
            raise forms.ValidationError(
                "Username length must be between 3 and 16 characters.",
                code='username_badlength',
            )
        if not re.match(r'^[\w]+$', username):
            raise forms.ValidationError(
                "Username may contain only letters and numbers characters.",
                code='username_notalpha',
            )
        return username

    def save(self, commit=True):
        user = super(UserCreationWithEmailForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
