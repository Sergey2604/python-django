from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from shopapp.models import Product, Order
from .forms import ProductForm, OrderForm, GroupForm


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            'products': products
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
    model = Product
    context_object_name = 'product'


class ProductsListView(ListView):
    template_name = 'shopapp/products_list.html'
    # model = Product
    context_object_name = 'products'
    queryset = Product.objects.filter(archieved = False)


class ProductCreateView(CreateView):
    model = Product
    fields = 'name', 'description', 'price', 'discount'
    success_url = reverse_lazy('shopapp:products_list')


class ProductUpdateView(UpdateView):
    model = Product
    fields = 'name', 'description', 'price', 'discount'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs = {'pk': self.object.pk}
        )


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


class OrdersListView(ListView):
    queryset = Order.objects.select_related('user').prefetch_related('products')


class OrderDetailView(DetailView):
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