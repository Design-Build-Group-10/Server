# Generated by Django 4.2.16 on 2024-10-15 01:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_user_browse_history_user_favorite_products_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'User'},
        ),
    ]
