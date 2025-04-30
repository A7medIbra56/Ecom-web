from django.shortcuts import render 
from django.contrib.auth.decorators import login_required
from ecommerce.users.models import User
from ecommerce.product.models import Product
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings

def home(request):
    
    newest_products = Product.objects.all()[0:8]
    
    context = {
        'newest_products': newest_products
    }
    
    return render(request, 'home.html', context)

def test_base_template(request):
    
    base_email = 'notifications/base_email.html'
    cart_view = 'cart/messages/order_placed.txt'
    all_auth_email_view = 'account/email/unknown_account_message.html'
    
    view = all_auth_email_view
    
    context = {
        'is_preview': True
    }
    
    html = render_to_string(view, context)
    
    return HttpResponse(html, content_type="text/html")