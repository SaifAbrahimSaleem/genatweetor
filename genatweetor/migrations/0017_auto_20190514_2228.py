# Generated by Django 2.1.5 on 2019-05-14 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0016_auto_20190514_1203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tweet',
            name='id',
        ),
        migrations.AlterField(
            model_name='tweet',
            name='tweetID',
            field=models.CharField(blank=True, max_length=200, primary_key=True, serialize=False),
        ),
    ]