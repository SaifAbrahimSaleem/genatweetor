# Generated by Django 2.1.5 on 2019-01-13 18:00

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tweetedBy', models.CharField(blank=True, max_length=100)),
                ('tweetText', models.CharField(blank=True, max_length=250)),
                ('tweetDate', models.DateTimeField(verbose_name='Date Tweeted')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('dob', models.DateTimeField(verbose_name='Date of Birth')),
                ('profileImage', models.ImageField(upload_to='profileImages')),
                ('tweetCount', models.IntegerField()),
                ('followerCount', models.IntegerField()),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]