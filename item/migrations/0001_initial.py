# Generated by Django 4.1.6 on 2023-07-21 10:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item.brand')),
            ],
            options={
                'unique_together': {('name', 'brand')},
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=30)),
                ('slug', models.SlugField(max_length=30, null=True)),
                ('item_photo', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('release_date', models.DateField()),
                ('display', models.BooleanField(default=False)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item.brand')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item.position')),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='item.series')),
            ],
        ),
    ]
