# Generated by Django 2.1.5 on 2019-05-14 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0017_auto_20190514_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='tweetID',
            field=models.AutoField(max_length=1000, primary_key=True, serialize=False),
        ),
    ]