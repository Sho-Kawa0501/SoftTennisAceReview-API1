# Generated by Django 4.2.7 on 2023-12-05 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_customuser_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='uuid',
            new_name='id',
        ),
    ]
