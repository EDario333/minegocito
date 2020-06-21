# Generated by Django 2.1.5 on 2019-02-22 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogues', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='disabled_reason',
            field=models.CharField(blank=True, default=None, max_length=1024, null=True, verbose_name='Indique la razón para inhabilitar este producto'),
        ),
        migrations.AlterField(
            model_name='products',
            name='dropped_reason',
            field=models.CharField(blank=True, default=None, max_length=1024, null=True, verbose_name='Indique la razón para eliminar este producto'),
        ),
    ]