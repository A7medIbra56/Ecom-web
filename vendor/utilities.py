from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
import os
from ecommerce.product.models import ProductImage
import json

def add_product(request, product_form):
    if product_form.is_valid():
        # Save product Data
        product = product_form.save(commit=False)
        product.vendor = request.user.vendor  # Assuming the user is a vendor
        product.is_approved = False  # Set to False by default
        product.save()

        # Save product images
        images = request.FILES.getlist("product_images")
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        messages.success(request, 'Added Product, it is sent for review. We will be back shortly')
        
        return redirect("vendor_dashboard:products_list")
    
    else:
        messages.error(request, "Form is invalid. Please correct the errors.")

def update_product(request, product_form, product):
    if product_form.is_valid():
        # Update form generally
        product_form.save()

        # Handle image Updating
        # Step 1: Get list of currently stored images from DB
        existing_images = set(product.images.values_list("image", flat=True))

        # Step 2: Get list of images supplied by FilePond (includes old ones)
        supplied_images = request.POST.get("existing_images", "[]")

        try:
            supplied_images = json.loads(supplied_images)  # Parse safely
        except json.JSONDecodeError:
            supplied_images = []

        # Ensure proper format: Extract only image paths
        supplied_images = set(
            img.replace("/media/", "") if isinstance(img, str) else img.get("source", "").replace("/media/", "")
            for img in supplied_images
        )

        # Step 3: Add new images from request.FILES (FilePond sends only new ones)
        uploaded_images = request.FILES.getlist("product_images")
        for image in uploaded_images:
            new_image = ProductImage.objects.create(product=product, image=image)
            supplied_images.add(new_image.image.name)  # Ensure it's included in the kept images

        # Step 4: Identify images to delete (in DB but missing from FilePond)
        images_to_delete = existing_images - supplied_images

        # Step 5: Delete removed images from DB and filesystem
        for image_path in images_to_delete:
            image_full_path = os.path.join(settings.MEDIA_ROOT, image_path)

            # Delete from DB
            ProductImage.objects.filter(product=product, image=image_path).delete()

            # Delete from filesystem
            if os.path.exists(image_full_path):
                os.remove(image_full_path)
                
        messages.success(request, "Product successfully updated.")

        return redirect("vendor_dashboard:products_list")
    
    else:
        messages.error(request, "Form is invalid. Please correct the errors.")
    
    
def get_order_highest_status(statuses, status_order):
    """
    Determine the highest status based on the order of statuses.
    """
    for status in reversed(status_order):  # Iterate in reverse order to find the highest status
        if status in statuses:
            return status
    return statuses[0]  # Default to the first status if none match.