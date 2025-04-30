from django.db import models
from django.templatetags.static import static
from django.conf import settings
import os
from vendor.models import Vendor
from django.utils.text import slugify
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_DOWN

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    ordering = models.IntegerField(default=0)
    commission_rate = models.FloatField(default=0.0)  # Default commission rate for this category

    class Meta:
        ordering = ['ordering']
    
    def __str__(self):
        return self.title
    
    
class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='sub_categories', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    commission_rate = models.FloatField(default=0.0)
    
    def save(self, *args, **kwargs):
        if not self.pk and self.commission_rate == 0.0:  # If it's a new object and commission_rate isn't set
            self.commission_rate = self.category.commission_rate
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
  
    
class Product(models.Model):
    # Basic product details
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=False)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    # Media files
    thumbnail = models.ImageField(upload_to='uploads/', blank=True, null=True)
    
    # Categorization & Specifications
    application_type = models.CharField(max_length=100, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    dimensions = models.CharField(max_length=50, blank=True, null=True)  # Example format: "L x W x H"
    weight = models.FloatField(default=0.0)  # Weight in grams or kg
    color = models.CharField(max_length=50, blank=True, null=True)
    texture = models.CharField(max_length=50, blank=True, null=True)
    
    # # Inventory Management
    stock_quantity = models.PositiveIntegerField(default=0)
    store_location = models.CharField(max_length=100, blank=True, null=True)
    
    # Shipping Details
    is_global = models.BooleanField(default=False)
    country_of_origin = models.CharField(max_length=100, blank=True, null=True)
    shipping_method = models.CharField(max_length=255, blank=True, null=True)
    shipping_sensitivity = models.CharField(max_length=50, blank=True, null=True)  # e.g., "Fragile", "Perishable"
    shipping_info = models.TextField(blank=True, null=True)
    
    # Pricing & Promotions
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_currency = models.CharField(max_length=10, default='SAR', blank=True, null=True)  # Default currency
    discount_percentage = models.FloatField(default=0)
    
    # Ratings & Reviews
    rating = models.CharField(max_length=10, blank=True, null=True)
    
    # Product verification
    is_approved = models.BooleanField(default=False)
    active = models.BooleanField(default=False, help_text="Indicates if the product is active and visible.")
    deactivated_by_admin = models.BooleanField(default=False, help_text="If True, only the admin can reactivate this product.")
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('REJECTED', 'Rejected'),
        ('ACTIVE', 'Active'),
        ('DEACTIVATED_VENDOR', 'Deactivated'),
        ('DEACTIVATED_ADMIN', 'Deactivated by Admin'), 
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', help_text="Current status of the product.")
    
    class Meta:
        ordering = ['-date_added']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # Convert title to slug
        super().save(*args, **kwargs)
    
    def get_thumbnail(self):
        if self.thumbnail:
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, self.thumbnail.name)
            if os.path.exists(thumbnail_path):  # ✅ Check if the file actually exists
                return self.thumbnail.url  # Return the valid URL

        # If nothing exists, return the default image
        return static('shared/img/image_not_found.png')
    
    def get_commission_earning(self):
        # Convert all monetary values to Decimal for precision
        item_price = self.price

        # Determine the commission rate
        if self.sub_category.commission_rate != 0.0:
            commission_rate = Decimal(str(self.sub_category.commission_rate))
        else:
            commission_rate = Decimal(str(self.category.commission_rate))

        # Correct formula: Divide item price by (1 + commission_rate/100) to ensure precision
        effective_vendor_earning = item_price / (Decimal("1.0") + (commission_rate / Decimal("100.0")))
        admin_item_commission = item_price - effective_vendor_earning

        admin_item_commission = admin_item_commission.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return f"{admin_item_commission} {self.price_currency}"
        
    def get_vendor_earning(self):
        # Convert all monetary values to Decimal for precision
        item_price = self.price

        # Determine the commission rate
        if self.sub_category.commission_rate != 0.0:
            commission_rate = Decimal(str(self.sub_category.commission_rate))
        else:
            commission_rate = Decimal(str(self.category.commission_rate))

        # Correct formula: Divide item price by (1 + commission_rate/100) to ensure precision
        effective_vendor_earning = item_price / (Decimal("1.0") + (commission_rate / Decimal("100.0")))
        
        # Round to 2 decimal places
        effective_vendor_earning = effective_vendor_earning.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return f"{effective_vendor_earning} {self.price_currency}"
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)

    # Customize the save method to generate unique filenames with this format:
    # <vendor.id>_<product.id>_<image.id>.<ext>
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if it's a new image
        super().save(*args, **kwargs)  # Save first to get an image ID

        if is_new and self.image:
            # Get vendor ID, product ID, and image ID
            vendor_id = self.product.vendor.id
            product_id = self.product.id
            image_id = self.id  # Now available after first save

            # Extract file extension
            ext = os.path.splitext(self.image.name)[1]

            # Generate new filename
            new_filename = f"{vendor_id}_{product_id}_{image_id}{ext}"
            os_new_path = os.path.join(settings.MEDIA_ROOT, "uploads/", new_filename)
            db_new_path = os.path.join("uploads/", new_filename)

            # Get the current file path
            old_path = self.image.path

            # Rename the file on disk
            if os.path.exists(old_path):  # Ensure file exists
                os.rename(old_path, os_new_path)

            # Update the image field with the new filename
            self.image.name = db_new_path
            super().save(update_fields=['image'])  # Save again with the new filename
    
    def __str__(self):
        return f"{self.product} - {self.image}"