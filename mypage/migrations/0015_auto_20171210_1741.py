# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-10 16:41
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mypage', '0014_auto_20171210_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movienight',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 12, 10, 17, 41, 37, 832460)),
        ),
    ]
