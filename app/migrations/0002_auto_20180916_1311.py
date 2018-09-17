# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-09-16 13:11
from __future__ import unicode_literals

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=cloudinary.models.CloudinaryField(blank=True, default='user.png', max_length=255, verbose_name='name'),
        ),
    ]
