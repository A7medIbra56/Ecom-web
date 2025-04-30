from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

"""
Signup:
- Full Name
- Email Adress
- Username
- Password
- Phone Number
- Date of Birth
"""

# Base User model that would be used for all user related models.
class User(AbstractUser):
    # Modify AbstractUser Model
    first_name = None
    last_name = None  
    
    email = models.EmailField(unique=True)
    
    # Custom User Data
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='customer'  # Customers sign up by default
    )

    def get_profile(self):
        """Returns the related profile model based on role"""
        if self.role == 'customer':
            return self.customer
        elif self.role == 'vendor':
            return self.vendor
        elif self.role == 'admin':
            return self.adminprofile
        return None
    
    
    class Meta:
        db_table = "users"

# Customer Model
class customer(models.Model):
    """
    Email
    Username
    Password
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='customer')
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        db_table = "customers"
        
        
class Address(models.Model):
    user = models.ForeignKey(customer, on_delete=models.CASCADE, related_name="addresses")
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)  # Default address

    def __str__(self):
        # Get all addresses for the user, ordered by their creation (id)
        user_addresses = list(self.user.addresses.order_by('id'))
        # Find the position (1-based index) of this address in the list
        address_number = user_addresses.index(self) + 1
        return f"Address No. {address_number} for user: {self.user}"

class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    user = models.ForeignKey(customer, on_delete=models.CASCADE, related_name="payment_methods")
    payment_type = models.CharField(choices=PAYMENT_TYPES, max_length=20)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)  # Last 4 digits for reference
    expiration_date = models.DateField(blank=True, null=True)
    is_default = models.BooleanField(default=False)  # Default payment method
    tokenized_id = models.CharField(max_length=255, blank=True, null=True)  # Store Stripe/PayPal token

    def __str__(self):
        # Get all addresses for the user, ordered by their creation (id)
        user_payment_methods = list(self.user.payment_methods.order_by('id'))
        # Find the position (1-based index) of this address in the list
        payment_method_number = user_payment_methods.index(self) + 1
        return f"Payment Method No. {payment_method_number} for user: {self.user}"
