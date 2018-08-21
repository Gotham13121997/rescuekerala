# Generated by Django 2.1 on 2018-08-21 17:32

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0069_auto_20180821_2231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='volunteer',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(error_messages={'invalid': 'Add + for International Phone Number'}, max_length=128, verbose_name='Phone - ഫോണ്\u200d നമ്പര്\u200d'),
        ),
    ]
