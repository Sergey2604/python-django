# coding=utf-8
from django import forms
from django.contrib.auth.models import User

from myauth.models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = 'bio', 'avatar'

