# Generated by Django 4.2.16 on 2024-10-14 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_detected',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
