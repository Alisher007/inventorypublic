# Generated by Django 3.1.5 on 2021-03-21 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_auto_20210321_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='barcode',
            field=models.CharField(default='n1016', max_length=150),
        ),
        migrations.DeleteModel(
            name='Barcode',
        ),
    ]