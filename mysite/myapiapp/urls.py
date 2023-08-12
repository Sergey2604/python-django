# coding=utf-8
from django.urls import path

from .views import hello_world_view, GroupsListView

app_name = 'api'

urlpatterns = [
    path('hello/', hello_world_view, name = 'hello'),
    path('groups/', GroupsListView.as_view(), name = 'groups')
]
