# Generated by Django 2.1.5 on 2019-05-14 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0018_auto_20190514_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='tweetID',
            field=models.IntegerField(blank=True, primary_key=True, serialize=False),
        ),
    ]
