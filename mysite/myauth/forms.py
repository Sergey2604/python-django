# coding=utf-8
from django import forms

from myauth.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = "__all__"

    images = forms.ImageField(
        widget = forms.ClearableFileInput({'multiple':True}))
