# Generated by Django 2.0.7 on 2018-08-15 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basedata', '0002_auto_20180815_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='active',
            field=models.BooleanField(default=True, verbose_name='状态'),
        ),
    ]
