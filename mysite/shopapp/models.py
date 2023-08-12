# coding=utf-8
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _, ngettext as __


def product_preview_directory_path(instance: 'Product', filename: str) -> str:
    return 'products/product_{pk}/preview/{filename}'.format(
        filename = filename,
        pk = instance.pk
    )


class Product(models.Model):
    class Meta:
        ordering = ['name']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    name = models.CharField(max_length = 100, verbose_name = _('название'))
    description = models.TextField(null = False, blank = True, verbose_name = _('описание'))
    price = models.DecimalField(default = 0, max_digits = 8, decimal_places = 2, verbose_name = _('цена'))
    discount = models.SmallIntegerField(default = 0, verbose_name = _('скидка'))
    created_at = models.DateField(auto_now_add = True, verbose_name = _('дата создания'))
    archieved = models.BooleanField(default = False, verbose_name = _('заархивировано?'))
    created_by = models.ForeignKey(User, on_delete = models.DO_NOTHING, blank = True, verbose_name = _('кем создано'))
    preview = models.ImageField(null = True, blank = True, upload_to = product_preview_directory_path,
                                verbose_name = _('превью'))

    def __str__(self) -> str:
        return f'Product (pk={self.pk}, name={self.name!r})'


def product_images_directory_path(instance: 'ProductImage', filename: str) -> str:
    return 'products/product_{pk}/images/{filename}'.format(
        filename = filename,
        pk = instance.product.pk
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = 'images')
    images = models.ImageField(upload_to = product_images_directory_path)
    description = models.CharField(max_length = 200, null = False, blank = True)


class Order(models.Model):
    delivery_address = models.TextField(null = True, blank = True, verbose_name = _('адрес доставки'))
    promocode = models.CharField(max_length = 20, null = False, blank = True, verbose_name = _('промокод'))
    created_at = models.DateField(auto_now_add = True, verbose_name = _('дата создания'))
    user = models.ForeignKey(User, on_delete = models.PROTECT, verbose_name = _('кем создан'))
    products = models.ManyToManyField(Product, related_name = 'orders', verbose_name = _('продукты в заказе'))
    receipt = models.FileField(null = True, blank = True, upload_to = 'orders/receipts/', verbose_name = _('чек'))

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
