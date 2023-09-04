# coding=utf-8
"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и т.д.
"""
from csv import DictWriter
from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, \
    JsonResponse
from django.shortcuts import render, redirect, reverse, get_list_or_404, \
    get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, \
    DeleteView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiResponse

from myauth.models import Profile
from shopapp.models import Product, Order, ProductImage
from .common import save_csv_products
from .forms import GroupForm, ProductForm
from .serializers import ProductSerializer, OrderSerializer

import logging


# log = logging.getLogger(__name__)


@extend_schema(description = 'Product views CRUD')
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.

    Полный CRUD для сущностей товара
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ['name', 'description']
    filterset_fields = [
        'name',
        'description',
        'price',
        'discount',
        'archieved'
    ]
    ordering_fields = [
        'name',
        'price',
        'discount',
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @extend_schema(
        summary = 'Get one product by ID',
        description = 'Retrieves **product**, returns 404 if not found',
        responses = {
            200: ProductSerializer,
            404: OpenApiResponse(
                description = 'Empty response, product by ID not found'
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods = ['get'], detail = False)
    def download_csv(self, request: Request) -> Response:
        filename = 'products-export.csv'
        response = HttpResponse('text/csv')
        response[
            'Content-Disposition'] = f'attachment;filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames = fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(methods = ['post'],
            detail = False,
            parser_classes = [MultiPartParser])
    def upload_csv(self, request: Request) -> Response:
        products = save_csv_products(
            file = request.FILES['file'].file,
            encoding = request.encoding,
        )
        serializer = self.get_serializer(products, many = True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_filter = ['products', 'delivery_address']
    filterset_fields = [
        'delivery_address',
        'promocode',
        'created_at',
        'user',
        'products',
    ]
    ordering_filters = ['delivery_address', 'user', 'products']


class ShopIndexView(View):

    # @method_decorator(cache_page(60 * 2))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            'products': products,
            'items': 1,
        }
        # log.debug('Products for shop index: %s', products)
        # log.info('Rendering shop index')
        print('Shop index context', context)
        return render(request, 'shopapp/shop-index.html', context = context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'form': GroupForm,
            'groups': Group.objects.prefetch_related('permissions').all()
        }
        return render(request, 'shopapp/groups-list.html', context = context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products_list.html'
    # model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archieved = False)


class ProductCreateView(
    CreateView):  # ��� ������������ ����������� PermissionRequiredMixin
    # permission_required = 'shopapp.add_product'
    model = Product
    fields = 'name', 'description', 'discount', 'price', 'preview'
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    # fields = 'name', 'description', 'price', 'discount', 'preview'
    template_name_suffix = '_update_form'
    form_class = ProductForm

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs = {'pk': self.object.pk}
        )

    def test_func(self):
        if self.request.user.is_superuser:
            return True

        self.object = self.get_object()

        has_edit_perm = self.request.user.has_perm("shopapp.change_product")
        created_by_current_user = self.object.created_by == self.request.user
        return has_edit_perm and created_by_current_user

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist('images'):
            ProductImage.objects.create(
                product = self.object,
                image = image
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archieved = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderCreateView(CreateView):
    model = Order
    fields = 'user', 'products', 'promocode', 'delivery_address'
    success_url = reverse_lazy('shopapp:orders_list')


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.select_related('user').prefetch_related(
        'products')


class OrderDetailView(PermissionRequiredMixin,
                      DetailView):  # закомментировал для тестов, не смог обойти
    permission_required = 'shopapp.view_order'
    queryset = Order.objects.select_related('user').prefetch_related(
        'products')


class OrderUpdateView(UpdateView):
    model = Order
    fields = 'user', 'products', 'promocode', 'delivery_address'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs = {'pk': self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class ProductsExportDataView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = 'products_data_export'
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    'pk': product.pk,
                    'name': product.name,
                    'price': product.price,
                    'archieved': product.archieved
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        elem = products_data[0]
        name = elem['name']
        print('name: ', name)
        return JsonResponse({'products': products_data})


class OrdersExportDataView(UserPassesTestMixin, View):
    def get(self, request: HttpRequest) -> JsonResponse:
        if self.request.user.is_staff:
            orders = Order.objects.order_by('pk').all()
            print('orders', orders)
            orders_data = [
                {
                    'pk': order.pk,
                    'delivery_address': order.delivery_address,
                    'promocode': order.promocode,
                    'user_id': order.user_id,
                    'products': [p.pk for p in order.products.all()]

                }
                for order in orders
            ]
            print('orders-data', orders_data)
            return JsonResponse({'orders': orders_data})
        print('У вас недостаточно прав для просмотра этой страницы')
        return JsonResponse(
            {'rules', 'У вас недостаточно прав для просмотра этой страницы'})

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class LatestProductsFeed(Feed):
    title = 'Latest products'
    description = 'Updates on changes and addition products'
    link = reverse_lazy('shopapp:products_list')

    def items(self):
        return (
            Product.objects
            .filter(created_at__isnull = False)
            .order_by('-created_at')[:5])

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]

    def item_link(self, item: Product):
        return reverse('shopapp:product_details', kwargs = {'pk': item.pk})


class UserOrdersListView(LoginRequiredMixin, ListView):
    # template_name = 'shopapp/order_list.html'

    def get_context_data(self, **kwargs):
        self.context = super().get_context_data()
        self.context['user'] = self.kwargs.get('Order.user')
        return self.context

    #
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        print(user_id)
        owner = Order.objects.filter(user_id = user_id).all()
        return owner

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = self.kwargs.get('user_id')
        context = {
            'user_id': user,
            'object_list': self.get_queryset(),
            'users': User.objects.filter(id = user)
        }
        if get_object_or_404(User, pk = user):
            return render(request, 'shopapp/order_list.html',
                          context = context)
        return render(request, 'shopapp/order_list.html', status = 404)


class UsersOrdersExportView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:

        user_id = self.kwargs.get('user_id')
        cache_key = 'orders_data_export'
        orders_data = cache.get(cache_key)
        if orders_data is None:
            orders = Order.objects.filter(user_id = user_id).all()
            orders_data = [
                {
                    'id': order.pk,
                    'delivery_address': order.delivery_address,
                    'promocode': order.promocode,
                    'user_id': order.user_id,
                    'created_at': order.created_at
                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 300)
        cache.delete(cache_key)
        print('user', user_id)
        elem = orders_data[0]
        pk = elem['id']
        print('id: ', pk)
        if get_object_or_404(User, pk = user_id):
            return JsonResponse({'orders': orders_data})
        return render(request, template_name = None, status = 404)
