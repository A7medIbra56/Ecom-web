from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from django.core.paginator import Paginator
from ecommerce.product.models import Product, ProductImage
from ecommerce.product.forms import ProductForm
from vendor.utilities import update_product, add_product
from shared.utilities import search_model  

class ProductsListView(ListView):
    model = Product
    template_name = "vendor_dashboard/products/product_list.html"
    context_object_name = "products"
    paginate_by = 10

    search_fields = ["title"] 

    def get_queryset(self):
        search_query = self.request.GET.get("q", "")
        queryset = Product.objects.filter(vendor=self.request.user.vendor)
        return search_model(queryset, search_query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("q", "")
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get("page", 1)
        products = paginator.get_page(page)

        context["products_pagination"] = products
        context["pagination_info"] = {
            "start": (products.start_index() if products else 0),
            "end": (products.end_index() if products else 0),
            "total": paginator.count,
        }
        context["search_query"] = search_query

        return context

# View vendor details
class ProductDetailView(DetailView):
    model = Product
    template_name = "vendor_dashboard/products/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.vendor != self.request.user.vendor:
            raise Http404("Page not found.")
        return obj

# Delete a product
class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("vendor_dashboard:products_list")

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        messages.success(request, "Product successfully deleted.")
        return redirect(self.success_url)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.vendor != self.request.user.vendor:
            raise Http404("Page not found.")
        return obj

# Create a new product
def product_create_view(request):
    if request.method == "POST":
        product_form = ProductForm(data=request.POST, files=request.FILES)
        add_product(request, product_form)
    else:
        product_form = ProductForm()

    context = {
        "product_form": product_form,
    }
    return render(request, "vendor_dashboard/products/product_create.html", context)

# Update an existing product
def product_update_view(request, pk):
    product = get_object_or_404(Product, pk=pk, vendor=request.user.vendor)

    if product.vendor != request.user.vendor:
        raise Http404("Page not found.")

    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        update_product(request, product_form, product)
    else:
        product_form = ProductForm(instance=product)

    context = {
        "form": product_form,
        "product": product
    }

    return render(request, "vendor_dashboard/products/product_edit.html", context)
