# Generated by Django 2.0.4 on 2018-05-14 05:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('personnel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='personnel.Employee')),
            ],
        ),
    ]
