# Generated by Django 3.0.3 on 2021-04-24 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0015_auto_20210424_1347'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('image', models.ImageField(upload_to='product_images')),
            ],
        ),
        migrations.DeleteModel(
            name='ColourVariation',
        ),
    ]
