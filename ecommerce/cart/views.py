import stripe 
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import Http404
from ecommerce.cart.cart import Cart
from ecommerce.cart.forms import CheckoutForm
from ecommerce.cart.utilities import create_order, post_checkout_tasks
from ecommerce.notifications.utils import send_email
from ecommerce.order.models import Order
from django.conf.urls import static

def cart(request):
    if request.user.role != "customer":
        raise Http404("You dont have authorization to access this page.")
    
    cart = Cart(request)

    remove_from_cart = request.GET.get('remove_from_cart', '')
    change_quantity = request.GET.get('change_quantity', '')
    quantity = request.GET.get('quantity', 0)

    if remove_from_cart:
        cart.remove(remove_from_cart)

        return redirect('cart')
    
    if change_quantity:
        cart.add(change_quantity, quantity, True)

        return redirect('cart')

    return render(request, 'cart/cart.html')


def checkout(request):
    if request.user.role != "customer":
        raise Http404("You dont have authorization to access this page.")
    
    cart = Cart(request)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            # Payment
            # stripe.api_key = settings.STRIPE_SECRET_KEY

            # stripe_token = form.cleaned_data['stripe_token']
            
            try:
                
                order_id = create_order(request, cart)
                
                # charge = stripe.Charge.create(
                #     amount=int(cart.get_total_cost() * 100),
                #     currency='USD',
                #     description='Charge from Interiorshop',
                #     source=stripe_token
                # )

                # print("Order Placed")
                
                post_checkout_tasks(order_id)
                
                send_email(
                    subject='Order Confirmation',
                    html_path='ecommerce/cart/messages/order_placed.html',
                    to_email=request.user.email,
                    context_data={
                        'request': request,
                        'user': request.user,
                        'cart': cart,
                        'order': Order.objects.get(id=order_id),
                        'total_cost': cart.get_total_cost(),
                    },
                )

                # Cart.clear()

                return redirect('success')
            
            except Exception as e:
                messages.error(request, f'There was something wrong with the payment {e}')
    else:
        form = CheckoutForm()

    return render(request, 'cart/checkout.html', {'form': form, 'stripe_pub_key': settings.STRIPE_PUB_KEY})


def success(request):
    return render(request, 'cart/success.html')