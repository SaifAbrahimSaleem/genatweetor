# Generated by Django 2.1.5 on 2019-03-07 04:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0005_auto_20190307_0310'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='profileImage',
        ),
    ]
