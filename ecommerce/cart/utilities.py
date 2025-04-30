from ecommerce.order.models import Order, OrderItem
from ecommerce.product.models import Product
from ecommerce.cart.cart import Cart
from vendor.models import Vendor
from django.conf import settings
from ecommerce.payment.utilities import create_transaction_records
from decimal import Decimal, ROUND_HALF_UP

def create_order(request, cart):
        
    order = Order.objects.create( 
        user = request.user.customer,
        # address = address,
        # zipcode = zipcode,
        # place = place,
        # phone = phone,
        paid_amount = cart.get_total_cost() 
    )
    
    for item in Cart(request):
        # Create each OrderItem and add its vendor to the order
        OrderItem.objects.create(
            order = order,
            product = item['product'],
            vendor = item['product'].vendor,
            price = item['product'].price,
            quantity = item['quantity']
        )
        
        # Edit stock level
        product = Product.objects.select_related('category', 'vendor').get(id=item['product'].id)
        product.stock_quantity -= item['quantity']
        product.stock_quantity = max(0, product.stock_quantity)  # Ensure stock doesn't go negative
        product.save()
        
        order.vendors.add(item['product'].vendor)
        
    return order.id

def notify_parties(order):
    # Place your notification logic here (e.g., emails to vendors and admin)
    pass

def post_checkout_tasks(order_id):
    """
    This function wraps the deferred processing tasks.
    In a real-world scenario, these tasks could be run asynchronously.
    """
    create_transaction_records(order_id)
    notify_parties(order_id)