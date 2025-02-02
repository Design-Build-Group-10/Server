# Generated by Django 4.2.16 on 2024-10-11 03:29

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('promotions', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('featured_products', models.ManyToManyField(related_name='featured_in_shops', to='product.product')),
            ],
        ),
    ]
