# Generated by Django 3.0.9 on 2020-08-23 07:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auctionlisting_buyer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auctionlisting',
            name='initial_bid',
        ),
        migrations.AlterField(
            model_name='bid',
            name='bid',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
