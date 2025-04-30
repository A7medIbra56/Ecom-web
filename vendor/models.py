from django.db import models
from django.contrib.auth import get_user_model

class Vendor(models.Model):
    # 1. Basic Vendor Information
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="vendor")
    business_name = models.CharField(max_length=255)
    # business_type = models.CharField(
    #     max_length=50,
    #     choices=[("Retailer", "Retailer"), ("Manufacturer", "Manufacturer"), ("Distributor", "Distributor")]
    # )
    business_registration_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    vat_tax_registration_number = models.CharField(max_length=100, blank=True, null=True)
    years_in_operation = models.PositiveIntegerField(default=0)

    # 2. Contact & Communication Details
    primary_contact_name = models.CharField(max_length=255, blank=True, null=True)
    business_phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_alternate_contact = models.CharField(max_length=20, blank=True, null=True)
    customer_support_email = models.EmailField(blank=True, null=True)

    # 3. Business & Operational Details
    business_address = models.TextField(blank=True, null=True)
    warehouse_locations = models.TextField(blank=True, null=True)  # If multiple, store as comma-separated values or JSON
    country_region_served = models.CharField(max_length=255, blank=True, null=True)
    logistics_partner = models.CharField(max_length=255, blank=True, null=True)

    # 4. Financial & Payment Information
    # payment_method_preferences = models.CharField(
    #     max_length=50,
    #     choices=[("Bank Transfer", "Bank Transfer")]
    # )
    # auto_payout_frequency = models.CharField(
    #     max_length=20,
    #     choices=[("Weekly", "Weekly"), ("By Request", "By Request"), ("Monthly", "Monthly")],
    #     default="Monthly"
    # )
    balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # Vendor's balance in the system
    pending_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # True if vendor has been paid for the order

    # # 5. Compliance & Certifications
    import_export_license = models.CharField(max_length=255, blank=True, null=True)
    iso_certification = models.BooleanField(default=False)  # True if vendor has ISO certification
    sustainability_certification = models.BooleanField(default=False)  # True if vendor is eco-friendly
    
    # # 6. Hidden Fields
    is_approved = models.BooleanField(default=False)  # Admin must approve vendors
    # approved_by = models.CharField(on_delete=models.SET_NULL, related_name="approved_by", null=True)
    # date_approved = models.DateTimeField(blank=True, null=True) 

    def __str__(self):
        return self.business_name
    
    class Meta:
        db_table = "vendors"
        # ordering = ['name']
    
    def get_balance(self):
        items = self.items.filter(vendor_paid=False, order__vendors__in=[self.id])
        return sum((item.product.price * item.quantity) for item in items)
    
    def get_paid_amount(self):
        items = self.items.filter(vendor_paid=True, order__vendors__in=[self.id])
        return sum((item.product.price * item.quantity) for item in items)
    
class Warehouse(models.Model):
    # Basic Information
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="warehouses", help_text="Vendor that owns this warehouse")
    name = models.CharField(max_length=255, help_text="Name of the warehouse")
    address = models.TextField(help_text="Full address of the warehouse")
    country = models.CharField(max_length=100, help_text="Country where the warehouse is located")
    city = models.CharField(max_length=100, help_text="City where the warehouse is located")
    postal_code = models.CharField(max_length=20, blank=True, null=True, help_text="Postal code of the warehouse")
    contact_number = models.CharField(max_length=20, blank=True, null=True, help_text="Contact number for the warehouse")
    email = models.EmailField(blank=True, null=True, help_text="Email address for the warehouse")
    google_maps_url = models.URLField(blank=True, null=True, help_text="Google Maps location URL for the warehouse")

    # Operational Details
    is_active = models.BooleanField(default=True, help_text="Indicates if the warehouse is active and operational")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the warehouse was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the warehouse was last updated")

    def __str__(self):
        return f"{self.name} - {self.vendor.business_name}"

    class Meta:
        ordering = ["-created_at"]

    def get_available_capacity(self):
        """Calculate and return the available capacity of the warehouse."""
        return self.capacity - self.current_stock

    def is_full(self):
        """Check if the warehouse is at full capacity."""
        return self.current_stock >= self.capacity