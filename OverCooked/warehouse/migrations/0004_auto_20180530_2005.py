# Generated by Django 2.0.4 on 2018-05-30 20:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0003_purchasedetail_left'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='junk',
            name='material',
        ),
        migrations.AddField(
            model_name='junk',
            name='storage',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='warehouse.Storage'),
            preserve_default=False,
        ),
    ]
