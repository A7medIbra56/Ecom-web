from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from ecommerce.users.models import Address, customer
from ecommerce.order.models import Order
from ecommerce.communication.models import CommunicationThread
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


# Profile Views
class AccountProfileView(LoginRequiredMixin, ListView):
    model = customer
    template_name = "account/profile/profile_list.html"
    context_object_name = "profile"
    login_url = '/login/'

    def get_queryset(self):
        return customer.objects.filter(user=self.request.user).get()


class AccountProfileEditView(LoginRequiredMixin, UpdateView):
    model = customer
    fields = ['first_name', 'last_name']  # Add fields as per your model
    template_name = "account/profile/profile_edit.html"
    success_url = reverse_lazy('account_home')
    login_url = '/login/'

    def get_object(self):
        return get_object_or_404(customer, user=self.request.user)



# Address Views
class AccountAddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = "account/addresses/addresses_list.html"
    context_object_name = "addresses"
    login_url = '/login/'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AccountAddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    fields = ['street', 'city', 'state', 'zip_code']  # Add fields as per your model
    template_name = "account/addresses/addresses_add.html"
    success_url = reverse_lazy('account_addresses')
    login_url = '/login/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AccountAddressEditView(LoginRequiredMixin, UpdateView):
    model = Address
    fields = ['street', 'city', 'state', 'zip_code']  # Add fields as per your model
    template_name = "account/addresses/addresses_edit.html"
    success_url = reverse_lazy('account_addresses')
    login_url = '/login/'
    
    def post(self, request, pk):
        """Handle actions: approve vendor, delete vendor, or submit ticket."""
        address = get_object_or_404(Address, pk=pk)
        action = request.POST.get("action")

        if action == "delete_address":
            address.delete()
            messages.success(request, "Vendor successfully deleted.")
            return redirect("admin_dashboard:vendor_list")





@login_required(login_url='/login/')
def account_orders(request):
    
    user = request.user
    customer_instance = customer.objects.get(user=user)

    # Filter addresses using the customer instance
    orders = Order.objects.filter(user=customer_instance)
    
    print(orders)
    
    context = {
        "orders": orders
    }
    
    return render(request, 'account/account_orders.html', context)


class AccountSupportTicketsList(LoginRequiredMixin, ListView):
    model = CommunicationThread
    template_name = "account/support/tickets_list.html"
    context_object_name = "tickets"
    paginate_by = 10
    login_url='/login/'

    def get_queryset(self):
        search_query = self.request.GET.get("q", "")
        
        query_set = CommunicationThread.objects.filter(
            user = self.request.user,
            # type="support_ticket", 
            # status__in=['open', 'awiating_admin_reply']
            ).order_by('-created_at')
                    
        
        if search_query:
            query_set = query_set.filter(subject__icontains=search_query)
            
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page', 1)
        tickets = paginator.get_page(page)

        context["tickets_pagination"] = tickets
        context["no_available_data"] = "There are no support tickets available"
        
        context["pagination_info"] = {
            "start": (tickets.start_index() if tickets else 0),
            "end": (tickets.end_index() if tickets else 0),
            "total": paginator.count,
        }
        
        context["search_query"] = self.request.GET.get("q", "")
        
        return context