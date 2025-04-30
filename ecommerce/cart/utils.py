from ecommerce.cart.cart import Cart

from ecommerce.order.models import Order, OrderItem

def checkout(request, first_name, last_name, email, address, zipcode, place, phone, amount):
    order = Order.objects.create(first_name=first_name, last_name=last_name, email=email, address=address, zipcode=zipcode, place=place, phone=phone, paid_amount=amount)

    for item in Cart(request):
        OrderItem.objects.create(order=order, product=item['product'], vendor=item['product'].vendor, price=item['product'].price, quantity=item['quantity'])

        # Add all the vendors assosiated with the order since vendors is a many to mant relationship. For example
        # Product 1 is from vwndor and product 2 is from vendor 2. So add both vendors to the order.
        order.vendors.add(item['product'].vendor)