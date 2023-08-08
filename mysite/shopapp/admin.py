from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .admin_mixins import ExportAsCSVMixin
from .models import Product, Order, ProductImage


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInline(admin.StackedInline):
    model = ProductImage

@admin.action(description='Archived products')
def mark_archieved(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archieved=True)


@admin.action(description='Unarchieved products')
def mark_unarchieved(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archieved=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [mark_archieved, mark_unarchieved, 'export_csv']
    inlines = [OrderInline,
               ProductInline,
               ]
    # list_display = 'pk', 'name', 'description', 'price', 'discount', 'created_at', 'archieved'
    list_display = 'pk', 'name', 'description_short', 'price', 'discount', 'created_at', 'archieved'
    list_display_links = 'pk', 'name', 'description_short'
    ordering = 'pk', 'name'
    search_fields = 'name', 'description'
    fieldsets = [
        (None, {
            'fields': ('name', 'description')
        }),
        ('Price options', {
            'fields': ('price', 'discount'),
            'classes': ('wide', 'collapse',),
        }),
        ('images', {
            'fields': ('preview',),
        }),
        ('Extra options', {
            'fields': ('archieved',),
            'classes': ('collapse',),
            'description': 'Extra options. Field "archieved" is for soft delete.'
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 50:
            return obj.description
        return obj.description[:50] + '...'


# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = 'delivery_address', 'promocode', 'created_at', 'user_verbose'
    list_display_links = 'delivery_address', 'promocode'

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')

    def user_verbose(self, obj: Order) -> str:
        return obj.user.username or obj.user.first_name
