# Generated by Django 2.1.5 on 2019-03-31 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0011_auto_20190331_1947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dob',
            field=models.DateTimeField(verbose_name='Date of Birth'),
        ),
    ]
