# from ecommerce.communication.models import CommunicationThread, CommunicationMessage
# from ecommerce.users.models import User

# # Fetch a user to associate with the threads
# user = User.objects.get(id=2)  # Replace with specific user logic if needed

# # Create two support ticket threads
# thread1 = CommunicationThread.objects.create(
#     type='support_ticket',
#     subject='Issue with Order #12345',
#     user=user,
#     status='open'
# )

# thread2 = CommunicationThread.objects.create(
#     type='support_ticket',
#     subject='Unable to Login to Account',
#     user=user,
#     status='in_progress'
# )

# # Add messages to the first thread
# CommunicationMessage.objects.create(
#     thread=thread1,
#     sender='user',
#     content='I am facing an issue with my order. Can you please help?'
# )

# CommunicationMessage.objects.create(
#     thread=thread1,
#     sender='admin',
#     content='Sure, we are looking into your issue. Please provide more details about the problem.'
# )

# CommunicationMessage.objects.create(
#     thread=thread1,
#     sender='user',
#     content='The order was delayed, and the product is damaged.'
# )

# # Add messages to the second thread
# CommunicationMessage.objects.create(
#     thread=thread2,
#     sender='user',
#     content='I am unable to log in to my account. It says the password is incorrect.'
# )

# CommunicationMessage.objects.create(
#     thread=thread2,
#     sender='admin',
#     content='We have reset your password. Please check your email for the new password.'
# )

# CommunicationMessage.objects.create(
#     thread=thread2,
#     sender='user',
#     content='Thank you! I was able to log in successfully.'
# )

# print("Demo data for CommunicationThread and CommunicationMessage has been created.")

# from django.contrib.auth import get_user_model
# from vendor.models import Vendor

# # Get the User model
# User = get_user_model()

# # Create a demo user
# user, created = User.objects.get_or_create(
#     username="vendor2",
#     defaults={
#         "email": "vendor2@example.com",
#         "is_active": True,
#     }
# )

# if created:
#     user.set_password("securepassword123")  # Set a password for the user
#     user.save()
#     print("Demo user 'vendor2' created successfully.")
# else:
#     print("User 'vendor2' already exists.")

# # Create a vendor associated with the user
# vendor, created = Vendor.objects.get_or_create(
#     user=user,
#     defaults={
#         "business_name": "Demo Vendor Business",
#         "business_registration_number": "REG123456",
#         "vat_tax_registration_number": "VAT987654",
#         "years_in_operation": 5,
#         "primary_contact_name": "John Doe",
#         "business_phone": "+1234567890",
#         "customer_support_email": "support@demovendor.com",
#         "business_address": "123 Demo Street, Demo City, Demo Country",
#         "country_region_served": "Global",
#         "logistics_partner": "Demo Logistics",
#         "balance": 1000.00,
#         "pending_balance": 200.00,
#         "iso_certification": True,
#         "sustainability_certification": False,
#         "is_approved": True,  # Mark the vendor as approved
#     }
# )

# if created:
#     print("Demo vendor created successfully.")
# else:
#     print("Vendor for user 'vendor2' already exists.")
    
    
from ecommerce.payment.models import Payout, AdminTransaction, VendorTransaction, PaymentReference
from ecommerce.order.models import Order
from decimal import Decimal

# Create a PaymentReference for the admin payout
admin_payment_reference, created = PaymentReference.objects.get_or_create(
    stripe_payment_id="admin_demo_stripe_id_12345",  # Replace with a unique Stripe ID
    defaults={
        "amount": Decimal("50.00"),  # Amount attempted for the payment
        "currency": "USD",  # Currency used for the payment
        "status": "SUCCESS",  # Status of the payment
        "raw_response": {
            "id": "admin_demo_stripe_id_12345",
            "object": "payment_intent",
            "amount": 5000,
            "currency": "usd",
            "status": "succeeded",
        },
    }
)

# Create a PaymentReference for the vendor payout
vendor_payment_reference, created = PaymentReference.objects.get_or_create(
    stripe_payment_id="vendor_demo_stripe_id_12345",  # Replace with a unique Stripe ID
    defaults={
        "amount": Decimal("450.00"),  # Amount attempted for the payment
        "currency": "USD",  # Currency used for the payment
        "status": "SUCCESS",  # Status of the payment
        "raw_response": {
            "id": "vendor_demo_stripe_id_12345",
            "object": "payment_intent",
            "amount": 45000,
            "currency": "usd",
            "status": "succeeded",
        },
    }
)

# Fetch existing transactions
admin_transaction = AdminTransaction.objects.get(id=12)  # Replace with the actual ID of the admin transaction
vendor_transaction = VendorTransaction.objects.get(id=12)  # Replace with the actual ID of the vendor transaction

# Create a Payout for the admin
admin_payout, created = Payout.objects.get_or_create(
    admin=admin_transaction,
    defaults={
        "amount": 50.00,
        "currency": "USD",
        "transaction_status": "SUCCESS",
        "payout_status": "REQUESTED",
        "payment_reference": admin_payment_reference,  # Link the payment reference
    }
)

# Create a Payout for the vendor
vendor_payout, created = Payout.objects.get_or_create(
    vendor=vendor_transaction,
    defaults={
        "amount": 450.00,
        "currency": "USD",
        "transaction_status": "SUCCESS",
        "payout_status": "REQUESTED",
        "payment_reference": vendor_payment_reference,  # Link the payment reference
    }
)

print("Demo payouts with payment references created successfully.")