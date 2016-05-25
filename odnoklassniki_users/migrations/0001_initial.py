# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('fetched', models.DateTimeField(db_index=True, null=True, verbose_name='\u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043e', blank=True)),
                ('id', models.BigIntegerField(help_text='\u0423\u043d\u0438\u043a\u0430\u043b\u044c\u043d\u044b\u0439 \u0438\u0434\u0435\u043d\u0442\u0438\u0444\u0438\u043a\u0430\u0442\u043e\u0440', serialize=False, verbose_name='ID', primary_key=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('shortname', models.CharField(max_length=100, db_index=True)),
                ('gender', models.PositiveSmallIntegerField(null=True, choices=[(1, '\u0436\u0435\u043d.'), (2, '\u043c\u0443\u0436.')])),
                ('birthday', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=200)),
                ('country', models.CharField(max_length=200)),
                ('country_code', models.CharField(max_length=20)),
                ('locale', models.CharField(max_length=5)),
                ('photo_id', models.BigIntegerField(null=True)),
                ('current_status', models.TextField()),
                ('current_status_date', models.DateTimeField(null=True)),
                ('current_status_id', models.BigIntegerField(null=True)),
                ('allows_anonym_access', models.NullBooleanField()),
                ('has_email', models.NullBooleanField()),
                ('has_service_invisible', models.NullBooleanField()),
                ('private', models.NullBooleanField()),
                ('last_online', models.DateTimeField(null=True)),
                ('registered_date', models.DateTimeField(null=True)),
                ('pic1024x768', models.URLField()),
                ('pic128max', models.URLField()),
                ('pic128x128', models.URLField()),
                ('pic180min', models.URLField()),
                ('pic190x190', models.URLField()),
                ('pic240min', models.URLField()),
                ('pic320min', models.URLField()),
                ('pic50x50', models.URLField()),
                ('pic640x480', models.URLField()),
                ('url_profile', models.URLField()),
                ('url_profile_mobile', models.URLField()),
            ],
            options={
                'verbose_name': 'Odnoklassniki user',
                'verbose_name_plural': 'Odnoklassniki users',
            },
            bases=(models.Model,),
        ),
    ]
