# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-09-16 16:18
from __future__ import unicode_literals

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20180916_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverinfo',
            name='scanned',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, verbose_name="picture of driver's liscence"),
        ),
    ]
