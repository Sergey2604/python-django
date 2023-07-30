from random import choices
from string import ascii_letters

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Product


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
        'shopapp/fixtures/fixtures-shopapp.json'
    ]

    def test_products_list(self):
        response = self.client.get(reverse('shopapp:products_list'))
        for product in Product.objects.filter(archieved = False).all():
            Product.created_by_id=User
            self.assertContains(response,product.name)
