# Generated by Django 2.1.5 on 2019-05-16 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('genatweetor', '0024_auto_20190516_1207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='engagementScore',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8),
        ),
    ]