# Generated by Django 4.2.7 on 2024-02-17 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0057_alter_exchange_fees'),
    ]

    operations = [
        migrations.AddField(
            model_name='send',
            name='denied',
            field=models.BooleanField(default=False, verbose_name='Отказано'),
        ),
    ]
