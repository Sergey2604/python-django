# coding=utf-8
from django.contrib.sitemaps import Sitemap

from shopapp.models import Product


class ShopSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Product.objects.filter(pub_date__isnull = False).order_by(
            '-created_at')

    def lastmod(self, obj: Product):
        return obj.created_at
