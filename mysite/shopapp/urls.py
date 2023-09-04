# coding=utf-8
from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .serializers import OrderSerializer
from .views import (ShopIndexView,
                    GroupsListView,
                    OrdersListView,
                    OrderCreateView,
                    ProductDetailsView,
                    ProductsListView,
                    OrderDetailView,
                    ProductCreateView,
                    ProductUpdateView,
                    ProductDeleteView,
                    OrderUpdateView,
                    OrderDeleteView,
                    ProductsExportDataView,
                    OrdersExportDataView,
                    ProductViewSet,
                    OrderViewSet,
                    LatestProductsFeed,
                    UserOrdersListView,
                    UsersOrdersExportView,
                    )

app_name = 'shopapp'

routers = DefaultRouter()
routers.register('product', ProductViewSet)
router_order = DefaultRouter()
router_order.register('order', OrderViewSet)

urlpatterns = [
    path('', ShopIndexView.as_view(), name = 'index'),
    path('groups/', GroupsListView.as_view(), name = 'groups_list'),
    path('products/', ProductsListView.as_view(), name = 'products_list'),
    path('orderapi/', include(router_order.urls), name = 'order_api'),
    path('api/', include(routers.urls), name = 'api'),
    path('products/create/', ProductCreateView.as_view(),
         name = 'create_product'),
    path('products/export/', ProductsExportDataView.as_view(),
         name = 'products-export'),
    path('products/latest/feed/', LatestProductsFeed(),
         name = 'products_feed'),
    path('products/<int:pk>/', ProductDetailsView.as_view(),
         name = 'product_details'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(),
         name = 'product_update'),
    path('products/<int:pk>/archive/', ProductDeleteView.as_view(),
         name = 'product_delete'),
    path('orders/', OrdersListView.as_view(), name = 'orders_list'),
    path('orders/create/', OrderCreateView.as_view(), name = 'create_order'),
    path('orders/export/', OrdersExportDataView.as_view(),
         name = 'orders-export'),
    path('orders/<int:pk>/', OrderDetailView.as_view(),
         name = 'order_details'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(),
         name = 'order_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(),
         name = 'order_delete'),
    path('orders/users/<int:user_id>/', UserOrdersListView.as_view(),
         name = 'users_orders'),
    path('orders/users/<int:user_id>/export/', UsersOrdersExportView.as_view(),
         name = 'users_orders_export')

]
