# Generated by Django 2.1.5 on 2019-04-21 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0013_tweet_usertweeted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='userTweeted',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='genatweetor.User'),
        ),
    ]
