# Generated by Django 2.1.5 on 2019-03-31 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0010_auto_20190330_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dob',
            field=models.DateTimeField(),
        ),
    ]
