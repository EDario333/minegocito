# Generated by Django 2.1.5 on 2019-02-26 08:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20190226_0223'),
        ('catalogues', '0002_auto_20190221_1830'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Brands',
        ),
        migrations.DeleteModel(
            name='Products',
        ),
    ]
