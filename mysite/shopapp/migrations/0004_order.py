# Generated by Django 4.2.3 on 2023-07-08 17:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('shopapp', '0003_product_archieved'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_address', models.TextField(blank=True, null=True)),
                ('promocode', models.CharField(blank=True, max_length=20)),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
    ]