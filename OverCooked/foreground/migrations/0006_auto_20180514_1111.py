# Generated by Django 2.0.4 on 2018-05-14 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foreground', '0005_auto_20180508_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detail',
            name='state',
            field=models.CharField(max_length=8),
        ),
    ]
