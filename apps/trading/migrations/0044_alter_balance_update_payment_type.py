# Generated by Django 4.2.7 on 2024-01-30 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0043_trader_subscription_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance_update',
            name='payment_type',
            field=models.CharField(blank=True, choices=[('Payme', 'Payme'), ('Click', 'Click')], max_length=255, null=True, verbose_name='Тип оплаты'),
        ),
    ]
