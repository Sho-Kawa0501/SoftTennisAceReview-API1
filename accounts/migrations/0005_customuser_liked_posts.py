# Generated by Django 4.1.6 on 2023-05-15 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_post_likes_count_like'),
        ('accounts', '0004_alter_customuser_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='liked_posts',
            field=models.ManyToManyField(related_name='liked_by', to='app.post'),
        ),
    ]
