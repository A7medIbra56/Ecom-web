from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.core.paginator import Paginator
from admin_dashboard.forms import *
from vendor.models import Vendor
from ecommerce.communication.models import CommunicationMessage, CommunicationThread, UploadedFile
from ecommerce.communication.forms import ReplyToThreadForm, StartThreadForm, ReplyToThreadWithFilesForm
from shared.utilities import search_model


# List all vendors
class VendorListView(ListView):
    model = Vendor
    template_name = "admin_dashboard/vendors/vendor_list.html"
    context_object_name = "vendors"
    paginate_by = 7
    
    search_fields = ["business_name", "phone_number"]
    
    def get_queryset(self):
        search_query = self.request.GET.get("q", "")
        query_set = Vendor.objects.filter(is_approved=True)
        return search_model(query_set, search_query)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page', 1)
        vendors = paginator.get_page(page)

        # Update context with pagination details
        context["vendors_pagination"] = vendors
        context["no_avaialable_data"] = "There are no vendors available"
        
        context["pagination_info"] = {
            "start": (vendors.start_index() if vendors else 0),
            "end": (vendors.end_index() if vendors else 0),
            "total": paginator.count,
        }
        
        context["search_query"] = self.request.GET.get("q", "")
        
        return context

# List only unapproved vendors
class ApproveVendorListView(ListView):
    model = Vendor
    template_name = "admin_dashboard/vendors/vendor_list.html"  # Reusing same list template
    context_object_name = "vendors"
    paginate_by = 7
    
    def get_queryset(self):
        search_query = self.request.GET.get("q", "")
        query_set = Vendor.objects.filter(is_approved=False)        
        return search_model(query_set, search_query)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page', 1)
        vendors = paginator.get_page(page)

        # Update context with pagination details
        context["vendors_pagination"] = vendors
        context["no_avaialable_data"] = "There are no Unapproved Vendors"
        
        context["pagination_info"] = {
            "start": (vendors.start_index() if vendors else 0),
            "end": (vendors.end_index() if vendors else 0),
            "total": paginator.count,
        }
        
        context["search_query"] = self.request.GET.get("q", "")
        
        return context

# View vendor details
class VendorDetailView(DetailView):
    model = Vendor
    template_name = "admin_dashboard/vendors/vendor_detail.html"
    context_object_name = "vendor"
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect to approval page if vendor is not approved."""
        vendor = self.get_object()
        if not vendor.is_approved:
            return redirect("admin_dashboard:vendor_approve", pk=vendor.pk)
        return super().dispatch(request, *args, **kwargs)
    
# Approve a vendor (Admin only)
class VendorApproveView(LoginRequiredMixin, View):
    def get(self, request, pk):
        """Show the vendor details and appropriate forms."""
        vendor = get_object_or_404(Vendor, pk=pk)
        thread = CommunicationThread.objects.filter(type='vendor_approval', vendor=vendor.user).first()
        thread_messages = CommunicationMessage.objects.filter(thread=thread)
        
        # If a thread exists, show the reply form; otherwise, show the start thread form
        if thread:
            reply_form = ReplyToThreadForm()
            return render(request, "admin_dashboard/vendors/vendor_detail.html", {
                "vendor": vendor,
                "thread": thread,
                "thread_messages": thread_messages,
                "reply_form": reply_form,
            })
        else:
            start_thread_form = StartThreadForm()
            return render(request, "admin_dashboard/vendors/vendor_detail.html", {
                "vendor": vendor,
                "start_thread_form": start_thread_form,
            })

    def post(self, request, pk):
        """Handle actions: approve vendor, delete vendor, or submit ticket."""
        vendor = get_object_or_404(Vendor, pk=pk)
        action = request.POST.get("action")

        if action == "approve_vendor":
            if request.user.role != "admin":
                return HttpResponseForbidden("You are not allowed to approve vendors.")
            vendor.is_approved = True
            vendor.save()
            messages.success(request, f"Vendor {vendor.business_name} has been approved.")
            return redirect("admin_dashboard:vendor_detail", pk=pk)

        elif action == "delete_vendor":
            vendor.delete()
            messages.success(request, "Vendor successfully deleted.")
            return redirect("admin_dashboard:vendor_list")

        elif action == "submit_ticket":
            thread = CommunicationThread.objects.filter(type='vendor_approval', vendor=vendor.user).first()

            # If a thread exists, handle the reply form
            if thread:
                reply_form = ReplyToThreadForm(request.POST)
                if reply_form.is_valid():
                    reply = reply_form.save(commit=False)
                    reply.thread = thread
                    reply.sender = "admin"  # Admin is the sender

                    if request.FILES.getlist('files'):
                        for file in request.FILES.getlist('files'):
                            uploaded_file = UploadedFile.objects.create(file=file)
                            reply.files.add(uploaded_file)
                    
                    reply.save()
                    messages.success(request, "Reply sent successfully.")
                else:
                    messages.error(request, "Failed to send reply.")
                return redirect("admin_dashboard:vendor_detail", pk=pk)

            # If no thread exists, handle the start thread form
            else:
                start_thread_form = StartThreadForm(request.POST)
                if start_thread_form.is_valid():
                    # Create the thread
                    thread = CommunicationThread.objects.create(
                        type="vendor_approval",
                        subject=start_thread_form.cleaned_data["subject"],
                        vendor=vendor.user,
                    )
                    # Create the first message
                    CommunicationMessage.objects.create(
                        thread=thread,
                        sender="admin",
                        content=start_thread_form.cleaned_data["message"],
                    )
                    messages.success(request, "New thread created successfully.")
                else:
                    messages.error(request, "Failed to create a new thread.")
                return redirect("admin_dashboard:vendor_detail", pk=pk)

        return redirect("admin_dashboard:vendor_detail", pk=pk)

# Update a vendor's details
class VendorUpdateView(UpdateView):
    model = Vendor
    form_class = VendorUpdateForm
    template_name = "admin_dashboard/vendors/vendor_edit.html"  # Generic form template
    success_url = reverse_lazy("admin_dashboard:vendor_list")
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect to approval page if vendor is not approved."""
        vendor = self.get_object()
        if not vendor.is_approved:
            return redirect("admin_dashboard:vendor_approve", pk=vendor.pk)
        return super().dispatch(request, *args, **kwargs)

# Delete a vendor
class VendorDeleteView(DeleteView):
    model = Vendor
    success_url = reverse_lazy("admin_dashboard:vendor_list")  # Redirect after deletion
    
    def post(self, request, *args, **kwargs):
        vendor = self.get_object()
        vendor.delete()
        messages.success(request, "Vendor successfully deleted.")
        return redirect(self.success_url)
