# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import django.db.models.deletion
import taggit.managers
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('popolo', '0001_initial'),
        ('candidator', '0005_auto_20170402_2003'),
        ('writeit', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('modelName', models.CharField(max_length=50, null=True, blank=True)),
                ('file', models.FileField(upload_to=b'attachments')),
                ('messageId', models.IntegerField(max_length=10, null=True)),
                ('author_id', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('person_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='popolo.Person')),
                ('extra_info', picklefield.fields.PickledObjectField(default={}, editable=False)),
                ('force_has_answer', models.BooleanField(default=False, help_text='Marca esto si quieres que el candidato aparezca como que no ha respondido')),
            ],
            options={
                'verbose_name': 'Candidato',
                'verbose_name_plural': 'Candidatos',
            },
            bases=('popolo.person', models.Model),
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extra_info', picklefield.fields.PickledObjectField(default={}, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('slug', autoslug.fields.AutoSlugField(populate_from=b'name', unique=True, editable=False)),
                ('description', models.TextField(blank=True)),
                ('searchable', models.BooleanField(default=True)),
                ('highlighted', models.BooleanField(default=False)),
                ('extra_info_title', models.CharField(max_length=50, null=True, blank=True)),
                ('extra_info_content', models.TextField(help_text='Puedes usar Markdown. <br/> <a href="http://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> allowed, but no raw HTML. Examples: **bold**, *italic*, indent 4 spaces for a code block.', max_length=3000, null=True, blank=True)),
                ('uses_preguntales', models.BooleanField(default=False, help_text='Esta elecci\xf3n debe usar preguntales?')),
                ('uses_ranking', models.BooleanField(default=False, help_text='Esta elecci\xf3n debe usar ranking')),
                ('uses_face_to_face', models.BooleanField(default=True, help_text='Esta elecci\xf3n debe usar frente a frente')),
                ('uses_soul_mate', models.BooleanField(default=True, help_text='Esta elecci\xf3n debe usar 1/2 naranja')),
                ('uses_questionary', models.BooleanField(default=True, help_text='Esta elecci\xf3n debe usar cuestionario')),
                ('area', models.ForeignKey(related_name='elections', to='popolo.Area', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Mi Elecci\xf3n',
                'verbose_name_plural': 'Mis Elecciones',
            },
        ),
        migrations.CreateModel(
            name='NouabookCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='NouabookItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250, null=True, blank=True)),
                ('text', models.TextField()),
                ('url', models.URLField(max_length=300, null=True, blank=True)),
                ('urlVideo', models.URLField(max_length=300, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('candidate', models.ForeignKey(to='elections.Candidate')),
                ('category', models.ForeignKey(to='elections.NouabookCategory')),
            ],
        ),
        migrations.CreateModel(
            name='PersonalData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=512)),
                ('value', models.CharField(max_length=1024)),
                ('candidate', models.ForeignKey(related_name='personal_datas', to='elections.Candidate')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionCategory',
            fields=[
                ('category_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='candidator.Category')),
                ('election', models.ForeignKey(related_name='categories', to='elections.Election', null=True)),
            ],
            options={
                'verbose_name': 'Categor\xeda de pregunta',
                'verbose_name_plural': 'Categor\xedas de pregunta',
            },
            bases=('candidator.category',),
        ),
        migrations.CreateModel(
            name='VotaInteligenteAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='VotaInteligenteMessage',
            fields=[
                ('message_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='writeit.Message')),
                ('moderated', models.NullBooleanField(default=None)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('fbshared', models.BooleanField(default=False)),
                ('author_ville', models.CharField(default=b'', max_length=35)),
                ('is_video', models.BooleanField(default=False)),
                ('moderated_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('first_moderation', models.BooleanField(default=False)),
                ('pending_status', models.BooleanField(default=False)),
                ('rejected_status', models.BooleanField(default=False)),
                ('election', models.ForeignKey(related_name='messages', default=None, to='elections.Election')),
                ('nouabookItem', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='elections.NouabookItem', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Message de question',
                'verbose_name_plural': 'Messages des questions',
            },
            bases=('writeit.message',),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
            ],
            options={
                'verbose_name': 'Pregunta',
                'proxy': True,
                'verbose_name_plural': 'Preguntas',
            },
            bases=('candidator.topic',),
        ),
        migrations.AddField(
            model_name='votainteligenteanswer',
            name='message',
            field=models.ForeignKey(related_name='answers', to='elections.VotaInteligenteMessage'),
        ),
        migrations.AddField(
            model_name='votainteligenteanswer',
            name='person',
            field=models.ForeignKey(related_name='answers', to='elections.Candidate'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='elections',
            field=models.ManyToManyField(related_name='candidates', null=True, to='elections.Election'),
        ),
    ]
