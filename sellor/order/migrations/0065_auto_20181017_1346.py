# Generated by Django 2.1.2 on 2018-10-17 18:46

from django.conf import settings
from django.db import migrations, models
import django_prices.models
import sellor.core
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0064_auto_20181016_0819'),
        ('payment', '0002_transfer_payment_to_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='discount_amount',
            field=django_prices.models.MoneyField(currency=settings.DEFAULT_CURRENCY, decimal_places=2, default=sellor.core.utils.taxes.zero_money, max_digits=12),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_gross',
            field=django_prices.models.MoneyField(currency=settings.DEFAULT_CURRENCY, decimal_places=2, default=sellor.core.utils.taxes.zero_money, max_digits=12),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_net',
            field=django_prices.models.MoneyField(currency=settings.DEFAULT_CURRENCY, decimal_places=2, default=sellor.core.utils.taxes.zero_money, max_digits=12),
        ),
        migrations.RemoveField(
            model_name='payment',
            name='order',
        ),
        migrations.DeleteModel(
            name='Payment',
        ),
        migrations.AlterField(
            model_name='orderevent',
            name='type',
            field=models.CharField(choices=[('PLACED', 'placed'), ('PLACED_FROM_DRAFT', 'draft_placed'), ('OVERSOLD_ITEMS', 'oversold_items'), ('ORDER_MARKED_AS_PAID', 'marked_as_paid'), ('CANCELED', 'canceled'), ('ORDER_FULLY_PAID', 'order_paid'), ('UPDATED', 'updated'), ('EMAIL_SENT', 'email_sent'), ('PAYMENT_CAPTURED', 'captured'), ('PAYMENT_REFUNDED', 'refunded'), ('PAYMENT_VOIDED', 'voided'), ('FULFILLMENT_CANCELED', 'fulfillment_canceled'), ('FULFILLMENT_RESTOCKED_ITEMS', 'restocked_items'), ('FULFILLMENT_FULFILLED_ITEMS', 'fulfilled_items'), ('TRACKING_UPDATED', 'tracking_updated'), ('NOTE_ADDED', 'note_added'), ('OTHER', 'other')], max_length=255),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='tax_rate',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.0'), max_digits=5),
        ),
    ]
