# Generated by Django 3.2.8 on 2024-06-06 14:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0004_alter_category_delete_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='delete_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
    ]
