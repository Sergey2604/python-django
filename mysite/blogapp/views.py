# coding=utf-8
from django.views.generic import ListView
from .models import Article


class BasedView(ListView):
    template_name = 'blogapp/article_list.html'
    model = Article
    context_object_name = 'article'
    queryset = Article.objects.prefetch_related().select_related().defer(
        'content')
