# Generated by Django 4.2.16 on 2024-10-02 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_remove_user_face_remove_user_groups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
