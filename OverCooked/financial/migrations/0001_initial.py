# Generated by Django 2.0.6 on 2018-07-02 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Total',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('flowType', models.CharField(max_length=32)),
                ('flow', models.DecimalField(decimal_places=2, max_digits=32)),
            ],
        ),
    ]
