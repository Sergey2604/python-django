from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
    Creates products
    """

    def handle(self, *args, **options):
        self.stdout.write('Create products')

        product_names = [
            'Laptop',
            'Desktop',
            'Smartphone'
        ]
        for prod in product_names:
            product, created = Product.objects.get_or_create(name=prod)
            self.stdout.write(f'Created product {product.name}')

        self.stdout.write(self.style.SUCCESS("Products created"))
