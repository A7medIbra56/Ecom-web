from django.shortcuts import render, redirect
from vendor.models import Vendor
from vendor.forms import VendorApplyForm
from ecommerce.users.forms import BaseAuthForm
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages

from ecommerce.communication.models import CommunicationThread, CommunicationMessage, UploadedFile
from ecommerce.communication.forms import ReplyToThreadForm, StartThreadForm, ReplyToThreadWithFilesForm
from ecommerce.order.models import Order
from django.db.models import Sum

def home(request):

    orders=Order.objects.all()
    total_orders = Order.objects.all().count()
    total_completed_orders = Order.objects.filter(status="FULLY_DELIVERED").count()
    total_pending_orders = Order.objects.filter(status="PREPARING").count()
    total_sales = Order.objects.filter(status='FULLY_DELIVERED').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
    returned_orders = Order.objects.filter(status='RETURNED_REFUNDED')
    total_refunds = Order.objects.filter(status='RETURNED_REFUNDED').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0

#   Total revenue (net)
    total_revenue = total_sales - total_refunds
    context = {
        'orders': orders,
        'total_orders': total_orders,
        "total_completed_orders": total_completed_orders,
        'total_pending_orders': total_pending_orders,
        'total_sales': total_sales,
        'returned_orders': returned_orders,
        "total_revenue": total_revenue,

    }
    return render(request, "vendor_dashboard/home.html", context)

def vendor_apply(request):
    
    if request.method == "POST":
        signup_form = BaseAuthForm("vendor", request.POST)
        vendor_form = VendorApplyForm(request.POST, request.FILES)
        
        if signup_form.is_valid() and vendor_form.is_valid():
            user = signup_form.save(request)
            
            Vendor.objects.create(
                user=user,
                is_approved=False,
                business_registration_number=vendor_form.cleaned_data["business_registration_number"],
                business_name=vendor_form.cleaned_data["business_name"]
            )
            
            return redirect("/")

    else:
        signup_form = BaseAuthForm("vendor")
        vendor_form = VendorApplyForm()

    return render(request, "vendor/vendor_apply.html", {"signup_form": signup_form, "vendor_form": vendor_form})


def approval_view(request):
    if request.user.role != "vendor":
        raise Http404("Page not found")

    # Fetch the thread for the vendor
    thread = CommunicationThread.objects.filter(type="vendor_approval", vendor=request.user).first()

    if not thread:
        # If no thread exists, render the page without a form
        return render(request, "vendor_dashboard/vendor_approval.html", {"thread": None})

    if request.method == "POST":
        reply_form = ReplyToThreadWithFilesForm(request.POST, request.FILES)
        if reply_form.is_valid():
            # Save the reply
            reply = reply_form.save(commit=False)
            reply.thread = thread
            reply.sender = "vendor"  # Vendor is the sender
            reply.save()

            # Handle file uploads
            for file in request.FILES.getlist("files"):
                UploadedFile.objects.create(message=reply, file=file)

            messages.success(request, "Your reply has been sent successfully.")
            return redirect("vendor_approval_page")  # Redirect to the same page
        else:
            messages.error(request, "Failed to send your reply. Please check the form.")
    else:
        reply_form = ReplyToThreadWithFilesForm()

    # Fetch all messages in the thread, sorted by timestamp (oldest to newest)
    thread_messages = CommunicationMessage.objects.filter(thread=thread).order_by("timestamp")

    context = {
        "thread": thread,
        "thread_messages": thread_messages,
        "reply_form": reply_form,
    }

    return render(request, "vendor_dashboard/vendor_approval.html", context)