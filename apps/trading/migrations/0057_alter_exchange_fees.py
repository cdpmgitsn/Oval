# Generated by Django 4.2.7 on 2024-02-13 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0056_alter_exchange_fees'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exchange',
            name='fees',
            field=models.FloatField(default=1, verbose_name='Комиссия'),
        ),
    ]
