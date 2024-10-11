# Generated by Django 4.2.16 on 2024-10-11 03:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('product', '0001_initial'),
        ('shop', '0001_initial'),
        ('user', '0008_user_robots'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='browse_history',
            field=models.ManyToManyField(blank=True, related_name='browsed_by_users', to='product.product'),
        ),
        migrations.AddField(
            model_name='user',
            name='favorite_products',
            field=models.ManyToManyField(blank=True, related_name='favorited_by_users', to='product.product'),
        ),
        migrations.AddField(
            model_name='user',
            name='followed_shops',
            field=models.ManyToManyField(blank=True, related_name='followed_by_users', to='shop.shop'),
        ),
        migrations.AddField(
            model_name='user',
            name='payment_method',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='shipping_address',
            field=models.TextField(blank=True, null=True),
        ),
    ]