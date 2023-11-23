# Generated by Django 4.2.7 on 2023-11-23 04:20

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('name', models.CharField(default='未設定', max_length=255)),
                ('image', models.ImageField(default='profile/default.png', upload_to='images')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
