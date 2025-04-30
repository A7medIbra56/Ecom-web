from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from ecommerce.payment.models import AdminTransaction, Payout
from admin_dashboard.models import PlatformFinance
from django.core.paginator import Paginator
from admin_dashboard.models import PlatformStats
from shared.utilities import search_model
# Home Page (FBV)
def earnings_home(request):

    admin_transactions = AdminTransaction.objects.all().order_by('-created_at')[:5]
    total_admin_transaction_count = AdminTransaction.objects.all().count()
    payouts = Payout.objects.all().order_by('-requested_at')[:5]

    context = {
        'platform_stats': PlatformStats,
        'platform_finance': PlatformFinance,
        'admin_transactions': admin_transactions,
        'total_admin_transaction_count': total_admin_transaction_count,
        'payouts': payouts,
    }
    
    return render(request, "admin_dashboard/earnings/home.html", context)

# Transaction List Page (CBV)
class TransactionListView(ListView):
    model = AdminTransaction
    template_name = "admin_dashboard/earnings/transaction/list.html"
    context_object_name = "transactions"
    paginate_by = 10

    search_fields = ["status", "commission_amount", "created_at"]

    def get_queryset(self):
        search_query = self.request.GET.get("q", "")
        query_set = AdminTransaction.objects.all()
        return search_model(query_set, search_query)
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_avaialable_data"] = "There are no Transactions available"
        
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page', 1)
        prodcuts = paginator.get_page(page)

        context["products_pagination"] = prodcuts

        context["pagination_info"] = {
            "start": (prodcuts.start_index() if prodcuts else 0),
            "end": (prodcuts.end_index() if prodcuts else 0),
            "total": paginator.count,
        }

        context["search_query"] = self.request.GET.get("q", "")
        
        return context

# Transaction Detail Page (CBV)
class TransactionDetailView(DetailView):
    model = AdminTransaction
    template_name = "admin_dashboard/earnings/transaction/detail.html"
    context_object_name = "transaction"

# Payout List Page (CBV)
class PayoutListView(ListView):
    model = Payout
    template_name = "admin_dashboard/earnings/payout/list.html"
    context_object_name = "payouts"
    paginate_by = 10
    
    search_fields = ["payout_status", "currency", "requested_at"]

    def get_queryset(self):
        search_query = self.request.GET.get("q", "")
        query_set = Payout.objects.all()
        return search_model(query_set, search_query)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_avaialable_data"] = "There are no Transactions available"
        
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page', 1)
        prodcuts = paginator.get_page(page)

        context["products_pagination"] = prodcuts

        context["pagination_info"] = {
            "start": (prodcuts.start_index() if prodcuts else 0),
            "end": (prodcuts.end_index() if prodcuts else 0),
            "total": paginator.count,
        }

        context["search_query"] = self.request.GET.get("q", "")
        
        return context

# Payout Detail Page (CBV)
class PayoutDetailView(DetailView):
    model = Payout
    template_name = "admin_dashboard/earnings/payout/detail.html"
    context_object_name = "payout"