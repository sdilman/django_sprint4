# Generated by Django 3.2.16 on 2024-12-17 20:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_comment_is_published'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='is_published',
        ),
    ]
