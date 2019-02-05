# Generated by Django 2.1.5 on 2019-01-18 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
        migrations.AddField(
            model_name='user',
            name='accountDescription',
            field=models.CharField(default='Admin Account', max_length=300),
        ),
        migrations.AlterField(
            model_name='user',
            name='followerCount',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='tweetCount',
            field=models.IntegerField(blank=True),
        ),
    ]
