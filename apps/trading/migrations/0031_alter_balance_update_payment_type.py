# Generated by Django 4.2.7 on 2024-01-20 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0030_exchange_wallet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance_update',
            name='payment_type',
            field=models.CharField(blank=True, choices=[('Payme', 'Payme'), ('Click', 'Click'), ('Ukassa', 'Ukassa')], max_length=255, null=True, verbose_name='Тип оплаты'),
        ),
    ]
