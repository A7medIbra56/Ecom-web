from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from ecommerce.product.models import Product
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.contrib import messages
from admin_dashboard.forms import ProductUpdateForm
from shared.utilities import search_model
from django.core.paginator import Paginator
from decimal import Decimal, ROUND_HALF_UP

# List all products
class ProductListView(ListView):
    model = Product
    template_name = "admin_dashboard/products/product_list.html"
    context_object_name = "products"
    paginate_by = 7

    search_fields = ["title"]
    
    def get_queryset(self):
        search_query = self.request.GET.get("q", "")
        query_set = Product.objects.filter(is_approved=True)
        return search_model(query_set, search_query)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_avaialable_data"] = "There are no products available"
        
        context["approval_page"] = False
        
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

# List only unapproved products
class ApproveProductListView(ListView):
    model = Product
    template_name = "admin_dashboard/products/product_list.html"  # Reusing same list template
    context_object_name = "products"
    paginate_by = 7

    search_fields = ["title"]
    
    def get_queryset(self):
        search_query = self.request.GET.get("q", "")
        query_set = Product.objects.filter(is_approved=False)
        return search_model(query_set, search_query)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["no_avaialable_data"] = "There are no unapproved products"
        
        context["approval_page"] = True

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

# View product details
class ProductDetailView(DetailView):
    model = Product
    template_name = "admin_dashboard/products/product_detail.html"
    context_object_name = "product"
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect to approval page if product is not approved."""
        product = self.get_object()
        if not product.is_approved:
            return redirect("admin_dashboard:product_approve", pk=product.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context

# Approve a product (Admin only)
class ProductApproveView(LoginRequiredMixin, View):
    
    def get(self, request, pk):
        """Show the approval button if accessed via GET instead of redirecting."""
        product = get_object_or_404(Product, pk=pk)

        # If the product is already approved, go to detail page
        if product.is_approved:
            return redirect("admin_dashboard:product_detail", pk=pk)

        return render(request, "admin_dashboard/products/product_detail.html", {"product": product})
    
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        action = request.POST.get("action")
        
        if request.user.role != "admin":
            return HttpResponseForbidden("You are not allowed to approve products.")

        if action == "approve":
            
            product.is_approved = True
            product.save() 
            
            messages.success(request, f"Product {product.title} has been approved.")
        
        return redirect("admin_dashboard:product_approve_list")

# Update a product's details
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductUpdateForm
    template_name = "admin_dashboard/products/product_edit.html"  # Generic form template
    success_url = reverse_lazy("admin_dashboard:product_list")
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect to approval page if product is not approved."""
        product = self.get_object()
        if not product.is_approved:
            return redirect("admin_dashboard:product_approve", pk=product.pk)
        return super().dispatch(request, *args, **kwargs)

# Delete a product
class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("admin_dashboard:product_list")  # Redirect after deletion
    
    def post(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        messages.success(request, "Product successfully deleted.")
        return redirect(self.success_url)
