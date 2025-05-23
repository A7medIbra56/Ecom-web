# Generated by Django 5.1.6 on 2025-04-25 03:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0002_paymentreference_payout"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="paymentreference",
            name="admin_transaction",
        ),
        migrations.RemoveField(
            model_name="paymentreference",
            name="vendor_transaction",
        ),
        migrations.RemoveField(
            model_name="payout",
            name="transaction_reference",
        ),
        migrations.RemoveField(
            model_name="payout",
            name="user",
        ),
        migrations.AddField(
            model_name="admintransaction",
            name="payment_reference",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="payment.paymentreference",
            ),
        ),
        migrations.AddField(
            model_name="payout",
            name="admin",
            field=models.ForeignKey(
                blank=True,
                help_text="Admin requesting the payout",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payouts",
                to="payment.admintransaction",
            ),
        ),
        migrations.AddField(
            model_name="payout",
            name="payment_reference",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="payment.paymentreference",
            ),
        ),
        migrations.AddField(
            model_name="payout",
            name="vendor",
            field=models.ForeignKey(
                blank=True,
                help_text="Vendor requesting the payout",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payouts",
                to="payment.vendortransaction",
            ),
        ),
        migrations.AddField(
            model_name="vendortransaction",
            name="payment_reference",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="payment.paymentreference",
            ),
        ),
    ]
