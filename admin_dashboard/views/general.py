from django.shortcuts import render
from ecommerce.product.models import Product
from vendor.models import Vendor
from ecommerce.users.models import customer
from ecommerce.payment.models import AdminTransaction
from ecommerce.order.models import Order
from django.db.models import Sum
from admin_dashboard.models import  PlatformStats
from ecommerce.communication.models import CommunicationThread

def home(request):
    #cards data
    
    #products for approval data
    products_for_approval = Product.objects.filter(is_approved=False).order_by('date_added')[:5]
    
    support_tickets = CommunicationThread.objects.filter(type='support_ticket', status__in=['awiating_admin_reply', 'open']).order_by('created_at')[:5]
    
    context = {
        'products_for_approval': products_for_approval,
        'support_tickets': support_tickets,
        'statistics': PlatformStats
    }

    return render(request, "admin_dashboard/home.html", context)