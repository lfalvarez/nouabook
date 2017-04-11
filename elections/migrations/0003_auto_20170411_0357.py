# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0002_auto_20170411_0325'),
    ]

    operations = [
        migrations.AddField(
            model_name='votainteligenteanswer',
            name='total_upvotes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='votainteligentemessage',
            name='total_upvotes',
            field=models.IntegerField(default=0),
        ),
    ]
