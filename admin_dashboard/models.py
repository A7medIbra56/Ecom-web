from django.db import models
from django.db.models import Sum
from ecommerce.product.models import Product
from vendor.models import Vendor
from ecommerce.users.models import customer
from ecommerce.payment.models import AdminTransaction
from ecommerce.order.models import Order
from ecommerce.communication.models import CommunicationThread

class PlatformSettings(models.Model):
    site_name = models.CharField(max_length=255, default="Area13 Marketplace")
    site_description = models.TextField(blank=True, null=True)
    support_email = models.EmailField(default="support@example.com")
    default_currency = models.CharField(max_length=10, default="USD")

    commission_rate = models.FloatField(default=10.0)  # percentage

    maintenance_mode = models.BooleanField(default=False)
    platform_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Platform Settings"
    
    class Meta:
        db_table = "platform_settings"
        
class PlatformFinance(models.Model):
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Platform Financials"
    
    class Meta:
        db_table = "platform_finance"

class PlatformStats(models.Model):
    this_month_new_customers = models.PositiveIntegerField(default=0)
    this_month_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    last_week_sales = models.PositiveIntegerField(default=0)
    this_week_sales = models.PositiveIntegerField(default=0)

    last_week_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    this_week_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Platform Stats"

    def sales_growth(self):
        if self.last_week_sales == 0:
            return ("up", 100) if self.this_week_sales > 0 else ("neutral", 0)

        change = self.this_week_sales - self.last_week_sales
        percent = (change / self.last_week_sales) * 100
        direction = "up" if change > 0 else "down"
        return (direction, round(abs(percent), 2))

    def revenue_growth(self):
        if self.last_week_revenue == 0:
            return ("up", 100) if self.this_week_revenue > 0 else ("neutral", 0)

        change = self.this_week_revenue - self.last_week_revenue
        percent = (change / float(self.last_week_revenue)) * 100
        direction = "up" if change > 0 else "down"
        return (direction, round(abs(percent), 2))
    
    def get_total_sales(self):
        """
        Returns the total number of delivered orders.
        """
        return Order.objects.filter(status='DELIVERED').count()

    def get_total_products(self):
        """
        Returns the total number of products.
        """
        return Product.objects.all().count()

    def get_total_vendors(self):
        """
        Returns the total number of vendors.
        """
        return Vendor.objects.all().count()

    def get_total_customers(self):
        """
        Returns the total number of customers.
        """
        return customer.objects.all().count()

    def get_total_revenue(self):
        """
        Returns the total revenue from successful admin transactions.
        """
        total_revenue = AdminTransaction.objects.filter(status='SUCCESS').aggregate(total=Sum('commission_amount'))['total']
        return total_revenue if total_revenue is not None else 0

    def get_products_for_approval(self, limit=5):
        """
        Returns a queryset of products pending approval, limited to the specified number.
        """
        return Product.objects.filter(is_approved=False).order_by('date_added')[:limit]

    def get_total_products_pending_approval(self):
        """
        Returns the total number of products pending approval.
        """
        return Product.objects.filter(is_approved=False).count()

    def get_support_tickets(self, limit=5):
        """
        Returns a queryset of support tickets awaiting admin reply or open, limited to the specified number.
        """
        return CommunicationThread.objects.filter(type='support_ticket', status__in=['awiating_admin_reply', 'open']).order_by('created_at')[:limit]