# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_data(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Election = apps.get_model("elections", "Election")
    BackgroundCategory = apps.get_model("elections", "BackgroundCategory")
    Background = apps.get_model("elections", "Background")
    PersonalData = apps.get_model("elections", "PersonalData")
    e = Election.objects.create(name='Marruecos2014', slug='marruecos2014')
    bc = BackgroundCategory.objects.create(id=1, name=u'Informations électorales', election=e)
    Background.objects.create(background_category=bc, id=1, name=u'Parti politique')
    Background.objects.create(background_category=bc, id=2, name=u'Circonscription')
    Background.objects.create(background_category=bc, id=3, name=u'Préfecture ou Province')
    Background.objects.create(background_category=bc, id=4, name=u"Date d'élection")
    Background.objects.create(background_category=bc, id=5, name=u'Expiration du mandat')

    bc = BackgroundCategory.objects.create(id=2, name=u'Affiliation au sein du Parlement', election=e)
    Background.objects.create(background_category=bc, id=6, name=u'Commission')
    Background.objects.create(background_category=bc, id=7, name=u'Groupe parlementaire')
    Background.objects.create(background_category=bc, id=8, name=u'Autres fonctions')
    Background.objects.create(background_category=bc, id=9, name=u'Ancienneté')

    bc = BackgroundCategory.objects.create(id=3, name=u'معلومات انتخابية', election=e)
    Background.objects.create(background_category=bc, id=10, name=u'الحزب')
    Background.objects.create(background_category=bc, id=11, name=u'الدائرة الانتخابية')
    Background.objects.create(background_category=bc, id=12, name=u'العمالة او الاقليم')
    Background.objects.create(background_category=bc, id=13, name=u'تاريخ الانتخاب')
    Background.objects.create(background_category=bc, id=14, name=u' تاريخ انتهاء النيابة')

    bc = BackgroundCategory.objects.create(id=4, name=u'الانتماء داخل المجلس', election=e)
    Background.objects.create(background_category=bc, id=15, name=u'اللجنة')
    Background.objects.create(background_category=bc, id=16, name=u'الفريق البرلماني')
    Background.objects.create(background_category=bc, id=17, name=u'مهام آخرى')
    Background.objects.create(background_category=bc, id=18, name=u'الأقدمية')

    bc = BackgroundCategory.objects.create(id=5, name=u'المعلومات الشخصية', election=e)
    Background.objects.create(background_category=bc, id=19, name=u'الاسم')
    Background.objects.create(background_category=bc, id=20, name=u'المهنة')
    Background.objects.create(background_category=bc, id=21, name=u'السيرة الذاتية')
    Background.objects.create(background_category=bc, id=22, name=u'مبادرات أخرى')
    Background.objects.create(background_category=bc, id=23, name=u'الوظائف العامة الأخرى')

    PersonalData.objects.create(id=1, label=u"Profession", election=e)
    PersonalData.objects.create(id=2, label=u"Biographie", election=e)
    PersonalData.objects.create(id=12, label=u"Autres initiatives", election=e)
    PersonalData.objects.create(id=13, label=u"Autres positions publiques", election=e)


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_data),
    ]
