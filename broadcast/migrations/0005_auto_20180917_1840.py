# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-09-17 18:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('broadcast', '0004_auto_20180917_0826'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='imagebroadcast',
            options={'ordering': ['description']},
        ),
        migrations.AlterModelOptions(
            name='textbroadcast',
            options={'ordering': ['message']},
        ),
    ]
