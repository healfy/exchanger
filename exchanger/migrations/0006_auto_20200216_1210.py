# Generated by Django 2.2.6 on 2020-02-16 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchanger', '0005_auto_20200214_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchangehistory',
            name='fee',
            field=models.DecimalField(decimal_places=8, default=0, max_digits=16, verbose_name='Transaction fee'),
        ),
    ]
