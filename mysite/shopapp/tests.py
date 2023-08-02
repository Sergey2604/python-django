import datetime
from random import choices
from string import ascii_letters
import json

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Product, Order


class ProductCreateViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username = 'bob_test', password = '12345')
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.product_name = ''.join(choices(ascii_letters, k = 10))
        Product.objects.filter(name = self.product_name).delete()
        self.client.login(**self.credentials)

    def test_create_product(self):
        response = self.client.post(
            reverse('shopapp:create_product'),
            {
                'name': self.product_name,
                'description': 'New Table',
                'discount': '5',
                'price': '150.99',
            }
        )
        self.assertRedirects(response, reverse('shopapp:products_list'))
        self.assertTrue(Product.objects.filter(name = self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username = 'bob-test', password = '12345')
        cls.user = User.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        self.product = Product.objects.create(name = 'Best product', created_by = self.user)

    def tearDown(self) -> None:
        self.product.delete()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse('shopapp:product_details', kwargs = {'pk': self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse('shopapp:product_details', kwargs = {'pk': self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'shopapp/fixtures/fixtures-product.json'
    ]

    def test_products_list(self):
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertQuerysetEqual(
            qs = Product.objects.filter(archieved = False).all(),
            values = (p.pk for p in response.context['products']),
            transform = lambda p: p.pk
        )
        self.assertTemplateUsed(response, 'shopapp/products_list.html')


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username = 'bob-test', password = '12345')
        cls.user = User.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_orders_list(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')

    def test_order_list_anonimous(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'shopapp/fixtures/fixtures-product.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(
            reverse('shopapp:products-export')
        )
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': str(product.price),
                'archieved': product.archieved
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data['products'],
            expected_data,
        )


class OrderDetailViewTestCase(TestCase):
    fixtures = [
        'shopapp/fixtures/fixtures-orders.json'
    ]

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username = 'Bob-test', password = '12345')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.shopapp_perm = Permission.objects.get(codename = 'view_order')
        cls.user.user_permissions.add(cls.shopapp_perm)

    def setUp(self) -> None:
        self.order = Order.objects.create(delivery_address = 'Lenina 22',
                                          created_at = datetime.datetime.now(),
                                          promocode = '12345',
                                          user_id = self.user.pk,
                                          )
        self.client.login(**self.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        print(self.user.user_permissions)
        response = self.client.get(
            reverse('shopapp:order_details', kwargs = {'pk': self.order.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Promocode')
        self.assertContains(response, 'Delivery address')
        for answer in response.context:
            if answer == self.order.pk:
                self.assertEquals(answer, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = ['myauth/fixtures/fixtures-users.json',
                'shopapp/fixtures/fixtures-orders.json',
                'shopapp/fixtures/fixtures-product.json']

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username = 'bob-test', password = '12345')
        cls.user = User.objects.create_user(**cls.credentials, is_staff = True)
        try:
            if not cls.user.is_staff:
                raise BaseException
        except BaseException('У вас недостаточно прав'):
            pass

    def setUp(self) -> None:
        self.client.login(**self.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def test_orders_export(self):
        response = self.client.get(
            reverse('shopapp:orders-export')
        )
        print(response)
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by('pk').all()
        expected_data = [
            {
                'pk': order.pk,
                'Delivery address': order.delivery_address,
                'Promocode': order.promocode,
                'user_id': order.user_id,
                'product_id': order.products.pk
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(
            orders_data['orders'],
            expected_data,
        )
        self.assertContains(response.context, ['Delivery address', 'pk', 'Promocode', 'user_id', 'Products.id'])
