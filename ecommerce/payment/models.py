from django.db import models
from django.conf import settings
from ecommerce.order.models import Order
from ecommerce.product.models import Product
from vendor.models import Vendor
from ecommerce.users.models import User

TRANSACTION_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('MISSING_ITEMS', 'Missing Items'),
    ('SUCCESS', 'Success'),
    ('FAILED', 'Failed'),
)

class PaymentReference(models.Model):
    """
    Stores the payment reference and details provided by the Stripe gateway.
    Useful for debugging and tracking payment issues.
    """    
    stripe_payment_id = models.CharField(max_length=255, unique=True, help_text="Unique payment ID provided by Stripe")
    amount = models.DecimalField(max_digits=8, decimal_places=2, help_text="Amount attempted for the payment")
    currency = models.CharField(max_length=10, help_text="Currency used for the payment")
    status = models.CharField(max_length=50, help_text="Status of the payment as returned by Stripe")
    raw_response = models.JSONField(help_text="Raw response data from Stripe for debugging purposes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Payment Reference (Stripe ID: {})".format(self.stripe_payment_id)

class OrderTransaction(models.Model):
    """
    Records the overall payment status for the order.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='transaction')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return "Order Transaction for Order #{}".format(self.order.id)


class VendorTransaction(models.Model):
    """
    Records the amount owed to a vendor for a particular order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='vendor_transactions')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_reference = models.ForeignKey(PaymentReference, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return "Vendor Transaction for Order #{}".format(self.order.id)


class AdminTransaction(models.Model):
    """
    Records the admin's commission per order in the order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='admin_transactions')
    commission_amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_reference = models.ForeignKey(PaymentReference, on_delete=models.CASCADE, null=True, blank=True)

    
    def __str__(self):
        return "Admin Transaction for Order #{}".format(self.order.id)

    
class Payout(models.Model):
    """
    Stores details of a payout request made from the dashboard.
    """
    PAYOUT_STATUS_CHOICES = (
        ('REQUESTED', 'Requested'),
        ('REVIEW', 'Reviewed by Admin'),
        ('SENT_TO_BANK', 'Sent to Bank'),
        ('MARK_AS_COMPLETE', 'Mark as Complete'),
    )

    admin = models.ForeignKey(AdminTransaction, on_delete=models.CASCADE, related_name='payouts', null=True, blank=True, help_text="Admin requesting the payout")
    vendor = models.ForeignKey(VendorTransaction, on_delete=models.CASCADE, related_name='payouts', null=True, blank=True, help_text="Vendor requesting the payout")
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount requested for the payout")
    currency = models.CharField(max_length=10, help_text="Currency of the payout")
    transaction_status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING', help_text="Transaction status of the payout request")
    payout_status = models.CharField(max_length=20, choices=PAYOUT_STATUS_CHOICES, default='REQUESTED', help_text="Current phase of the payout process")
    requested_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the payout was requested")
    processed_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when the payout was processed")
    payment_reference = models.ForeignKey(PaymentReference, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.admin:
            return "Payout Request by Admin #{} for Amount: {}".format(self.admin.id, self.amount)
        elif self.vendor:
            return "Payout Request by Vendor #{} for Amount: {}".format(self.vendor.id, self.amount)