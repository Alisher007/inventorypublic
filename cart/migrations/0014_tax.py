# Generated by Django 3.0.3 on 2021-04-23 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0013_auto_20210423_1424'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('percent', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'Taxes',
            },
        ),
    ]
