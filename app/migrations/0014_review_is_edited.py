# Generated by Django 4.1.6 on 2023-11-14 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_rename_like_favorite_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='is_edited',
            field=models.BooleanField(default=False),
        ),
    ]
