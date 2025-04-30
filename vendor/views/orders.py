from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import Http404
from django.db import transaction
from django.db.models import Q, Count, Case, When
from django.conf import settings
from ecommerce.payment.utilities import release_funds_task, release_funds
from django.views.decorators.cache import never_cache
from ecommerce.order.models import Order, OrderItem, ORDER_STATUS, ORDER_ITEM_STATUS
from vendor.models import Vendor
from django.db import connection
from datetime import timedelta
from django.utils.timezone import now
from base.tasks import sample_task
from vendor.utilities import get_order_highest_status

class OrdersListView(ListView):
    model = Order
    template_name = "vendor_dashboard/orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 10
    
    def get_queryset(self):
        vendor_orders = Order.objects.filter(vendors=self.request.user.vendor).order_by("-created_at")
        
        # Annotate orders with the count of undelivered items for the vendor
        vendor_orders = vendor_orders.annotate(
            undelivered_items_count=Count(
                Case(
                    When(
                        Q(items__vendor=self.request.user.vendor) & ~Q(items__status='DELIVERED'),
                        then=1
                    )
                )
            )
        )
        
        # Exclude orders where all items for the vendor are delivered
        return vendor_orders.filter(undelivered_items_count__gt=0)

def order_detail_view(request, pk):
    global is_all_vendor_items_delivered
    
    vendor = get_object_or_404(Vendor, user=request.user)
    order = Order.objects.prefetch_related("items").get(pk=pk)
    vendor_order_items = OrderItem.objects.select_related('product').filter(order=order, vendor=vendor)
    
    # Check if all items assigned to vendor are delivered
    is_all_vendor_items_delivered = all(item.status == 'DELIVERED' for item in vendor_order_items)
    
    if request.method == "POST":
        
        with transaction.atomic():
            # Update individual item statuses only if the order status was not changed
            for item in vendor_order_items:
                status_key = f"status_{item.id}"
                if status_key in request.POST:
                    new_status = request.POST[status_key]
                    if new_status != item.status:  # Only update if the status has changed
                        item.status = new_status
                        item.save()
                        messages.success(request, f"Status for item {item.product.title} updated to {item.get_status_display()}.")

            # Update the order status based on the statuses of its items
            item_statuses = vendor_order_items.values_list('status', flat=True)
            status_order = [status[0] for status in ORDER_ITEM_STATUS]
            highest_status = get_order_highest_status(item_statuses, status_order)
            if order.status != highest_status:  # Only update if the status has changed
                order.status = highest_status
                order.save()
                messages.success(request, f"Order status updated to {order.get_status_display()}.")
            
            # Refresh the order instance to get the latest status
            order.refresh_from_db()
            
            is_all_vendor_items_delivered = all(item.status == 'DELIVERED' for item in vendor_order_items)
            
            if is_all_vendor_items_delivered:
                #Check if all items are now delivered.
                if all(item.status == "DELIVERED" for item in order.items.all()):
                    order.status = "FULLY_DELIVERED"
                    order.save()
                
                # Schedule releasing funds if all items are delivered        
                if settings.DEBUG:
                    release_funds(order, vendor)
                
                else:
                    release_funds_task.apply_async(
                        args=[order.id, vendor.id],
                        eta=now() + timedelta(days=15)  # Schedule the task 15 days from now
                    )
                
                return redirect(request.path_info)   
    
    if is_all_vendor_items_delivered:
        messages.info(request, message="All items are delivered. Remeaining 15 days until funds are released.", extra_tags='order_status_message')
      
    # Custom view specific messages  
    view_message_storage = get_messages(request)
    page_messages = [msg for msg in view_message_storage if "order_status_message" in msg.tags]
    
    context = {
        "order": order,
        "order_status": ORDER_STATUS,
        "order_items": vendor_order_items,
        "order_items_status": ORDER_ITEM_STATUS,
        "order_status_messages": page_messages,
        "disable_order_editing": is_all_vendor_items_delivered
    }

    return render(request, "vendor_dashboard/orders/order_detail.html", context)

