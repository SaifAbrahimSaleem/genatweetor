# Generated by Django 2.1.5 on 2019-01-18 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0002_auto_20190118_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='accountDescription',
            field=models.CharField(max_length=300),
        ),
    ]
