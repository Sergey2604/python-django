# coding=utf-8
from django.contrib.syndication.views import Feed
from django.views.generic import ListView, DetailView
from .models import Article

from django.urls import reverse, reverse_lazy


class BasedView(ListView):
    template_name = 'blogapp/article_list.html'
    model = Article
    context_object_name = 'article'
    queryset = Article.objects.prefetch_related().select_related().defer(
        'content')


class ArticlesListView(ListView):
    queryset = (
        Article.objects
        .filter(pub_date__isnull = False)
        .order_by('-pub_date')
    )


class ArticleDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = 'Blog articles (latest)'
    description = 'Updates on changes and addition blog articles'
    link = reverse_lazy('blogapp:articles')

    def items(self):
        return (
            Article.objects
            .filter(pub_date__isnull = False)
            .order_by('-pub_date')[:5])

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]

    def item_link(self, item: Article):
        return reverse('blogapp:article_detail', kwargs = {'pk': item.pk})
