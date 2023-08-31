# coding=utf-8
from django.urls import path

from blogapp.views import BasedView, \
    ArticleDetailView, \
    LatestArticlesFeed

app_name = 'blogapp'

urlpatterns = [
    path('articles/', BasedView.as_view(), name = 'articles'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(),
         name = 'article_detail'),
    path('articles/latest/feed/', LatestArticlesFeed(),
         name = 'blog_last_feed')
]
