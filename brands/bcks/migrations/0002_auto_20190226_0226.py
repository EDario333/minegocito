# Generated by Django 2.1.5 on 2019-02-26 08:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brands', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brands',
            name='created_at',
            field=models.TimeField(default=datetime.datetime(2019, 2, 26, 2, 26, 44, 369454)),
        ),
        migrations.AlterField(
            model_name='brands',
            name='created_when',
            field=models.DateField(default=datetime.datetime(2019, 2, 26, 2, 26, 44, 369454)),
        ),
    ]
