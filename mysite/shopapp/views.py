# coding=utf-8
from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from shopapp.models import Product, Order, ProductImage
from .forms import GroupForm, ProductForm
from .serializers import ProductSerializer, OrderSerializer


class ProductViewSet(ModelViewSet):
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


class ProductCreateView(CreateView):  # ��� ������������ ����������� PermissionRequiredMixin
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
    queryset = Order.objects.select_related('user').prefetch_related('products')


class OrderDetailView(PermissionRequiredMixin, DetailView):  # закомментировал для тестов, не смог обойти
    permission_required = 'shopapp.view_order'
    queryset = Order.objects.select_related('user').prefetch_related('products')


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
        return JsonResponse({'rules', 'У вас недостаточно прав для просмотра этой страницы'})

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False
