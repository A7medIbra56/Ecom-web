from django.db import models

from ecommerce.product.models import Product
from vendor.models import Vendor

from ecommerce.users.models import customer

ORDER_STATUS = [
    ('CONFIRMED', 'Order Confirmed'),
    ('PREPARING', 'Preparing'),
    
    ('OUT_FOR_DELIVERY', 'Partially Out for Delivery'),
    ('DELIVERED', 'Partially Delivered'),
    ('FULLY_DELIVERED', 'Delivered'),
    
    ('RETURN_REQUESTED', 'Return Requested'),
    ('RETURNED_REFUNDED', 'Returned & Refunded'),
    
    ('CANCELED_BY_VENDOR', 'Canceled by Vendor'),
    ('CANCELED_BY_CUSTOMER', 'Canceled by Customer'),
]

ORDER_ITEM_STATUS = [
    ('CONFIRMED', 'Item Confirmed'),
    ('PREPARING', 'Preparing'),
    
    ('OUT_FOR_DELIVERY', 'Out for Delivery'),
    ('DELIVERED', 'Delivered'),
    
    ('RETURN_REQUESTED', 'Return Requested'),
    ('RETURNED_REFUNDED', 'Returned & Refunded'),
    
    ('CANCELED_BY_VENDOR', 'Canceled by Vendor'),
    ('CANCELED_BY_CUSTOMER', 'Canceled by Customer'),
]

class Order(models.Model):
    user = models.ForeignKey(customer, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True)
    # address = models.CharField(max_length=100)
    # zipcode = models.CharField(max_length=100)
    # place = models.CharField(max_length=100)
    # phone = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=255, choices=ORDER_STATUS, default='CONFIRMED')  # Overall order status
    vendors = models.ManyToManyField(Vendor, related_name='orders')

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='items', on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, related_name='items', on_delete=models.CASCADE)
    vendor_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=255, choices=ORDER_ITEM_STATUS, default='CONFIRMED')  # Overall order item status set by vendor for items
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return '%s' % self.id
    
    def get_total_price(self):
        return float(self.price*self.quantity)