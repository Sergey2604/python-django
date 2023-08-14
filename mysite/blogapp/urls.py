# coding=utf-8
from django.urls import path

from blogapp.views import BasedView

app_name = 'blogapp'

urlpatterns = [
    path('index/', BasedView.as_view(), name = 'index')
]
