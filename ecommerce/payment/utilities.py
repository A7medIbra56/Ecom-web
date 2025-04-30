from ecommerce.order.models import Order, OrderItem
from ecommerce.payment.models import VendorTransaction, AdminTransaction, PaymentReference
from vendor.models import Vendor
from decimal import Decimal, ROUND_HALF_DOWN, ROUND_HALF_UP
from django.contrib import messages
from django.db import transaction
from celery import shared_task

def create_transaction_records(order_id):  
    
    try:
        # Create payment refrence (DEMO)
        payment_reference, created = PaymentReference.objects.get_or_create(
            stripe_payment_id="demo_stripe_id_12345",  # Replace with a unique Stripe ID
            defaults={
                "amount": Decimal("500.00"),  # Amount attempted for the payment
                "currency": "USD",  # Currency used for the payment
                "status": "SUCCESS",  # Status of the payment
                "raw_response": {
                    "id": "demo_stripe_id_12345",
                    "object": "payment_intent",
                    "amount": 50000,
                    "currency": "usd",
                    "status": "succeeded",
                },  # Example raw response from Stripe
            }
        )
        
        order = Order.objects.prefetch_related('vendors').get(id=order_id)
        
        admin_sale_commision = 0

        # Create vendor transaction records.
        for vendor in order.vendors.all():
            
            vendor_sale_earnings = Decimal("0.0")
            
            vendor_items = OrderItem.objects.filter(vendor=vendor, order=order)
            
            for item in vendor_items:
                
                # Convert all monetary values to Decimal for precision
                item_price = Decimal(str(item.get_total_price()))

                # Determine the commission rate
                if item.product.sub_category.commission_rate != 0.0:
                    commission_rate = Decimal(str(item.product.sub_category.commission_rate))
                else:
                    commission_rate = Decimal(str(item.product.category.commission_rate))

                # Correct formula: Divide item price by (1 + commission_rate/100) to ensure precision
                effective_vendor_earning = item_price / (Decimal("1.0") + (commission_rate / Decimal("100.0")))
                admin_item_commission = item_price - effective_vendor_earning

                # Round to 2 decimal places
                effective_vendor_earning = effective_vendor_earning.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                admin_item_commission = admin_item_commission.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                # Update total earnings
                vendor_sale_earnings += effective_vendor_earning
                admin_sale_commision += admin_item_commission
            
            # Create transaction record and add money to pending balance
            VendorTransaction.objects.create(
                order = order,
                vendor = vendor,
                amount = vendor_sale_earnings,
                status = 'PENDING',  # update later on payment confirmation
                payment_reference = payment_reference  # Link to the payment reference
            )
            
            vendor = Vendor.objects.get(id=vendor.id)
            vendor.pending_balance += vendor_sale_earnings
            vendor.save()
            
        AdminTransaction.objects.create(
            order = order,
            commission_amount = admin_sale_commision,
            status = 'PENDING',
            payment_reference = payment_reference  # Link to the payment reference
        )
        
    except Exception as e:
        print(f"Error: {e}, at line {e.__traceback__.tb_lineno}")
        raise Exception(f"Error in create_transaction_records: {e}")

def release_funds(order, vendor):
    """
    Script to release funds to vendors and admin for delivered orders.
    
    PS:
    The following script follows the release funds workflow only. But in practicality, 
    when the order status is changed to delivered there is a 15 day wait until the funds are released to the vendors.
    This is to ensure that the customer does not return the product and the vendor does not get charged for the return.
    
    Notes:
    
    - Error Handling for Fund Release:
    Problem: If a fund release fails (e.g., due to database or payment gateway issues), 
    it could leave the system in an inconsistent state.
    Solution: Implement retry mechanisms and logging for failed fund releases.
    
    
    - Notification System:
    Problem: Vendors and customers may not always be aware of status changes.
    Solution: Add notifications (e.g., email or SMS) for key events like status updates, 
    fund releases, or delays.
    """ 
    
    with transaction.atomic():  # Ensure atomicity for database updates
        sale_vendor_transaction = VendorTransaction.objects.get(order=order, vendor=vendor)
        
        if sale_vendor_transaction:
            # Update vendor's balance
            old_pending_balance = vendor.pending_balance
            old_balance = vendor.balance
            
            vendor.pending_balance -= sale_vendor_transaction.amount
            vendor.balance += sale_vendor_transaction.amount
            vendor.pending_balance = max(Decimal('0.00'), vendor.pending_balance)
            vendor.save()
            
            new_pending_balance = vendor.pending_balance
            new_balance = vendor.balance
            
            # Update vendor transaction record
            sale_vendor_transaction.status = "SUCCESS"
            
            sale_vendor_transaction.save()

    # Release funds to admin only if all items are delivered
    if order.status == "FULLY_DELIVERED":
        admin_transaction = AdminTransaction.objects.select_related('order').get(order=order)
        
        if admin_transaction:
            # Mark admin transaction as successful
            admin_transaction.status = 'SUCCESS'
            admin_transaction.save()
            
@shared_task
def release_funds_task(order_id, vendor_id):
    """
    Celery task to release funds to vendors and admin for delivered orders.
    """
    from ecommerce.order.models import Order
    from vendor.models import Vendor

    order = Order.objects.get(id=order_id)
    vendor = Vendor.objects.get(id=vendor_id)

    # Call the original release_funds function
    release_funds(order, vendor)