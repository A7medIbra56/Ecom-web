from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from admin_dashboard.forms import CategoryForm, SubCategoryForm
from ecommerce.product.models import Category, SubCategory
from django.contrib import messages
from shared.utilities import search_model

# List all categories
class CategoryListView(ListView):
    model = Category
    template_name = "admin_dashboard/categories/categories_list.html"
    context_object_name = "categories"
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("q", "")
        return search_model(queryset, search_query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context

# View category details
class CategoryDetailView(DetailView):
    model = Category
    template_name = "admin_dashboard/categories/categories_detail.html"
    context_object_name = "category"

# Add category
class CategoryAddView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "admin_dashboard/categories/categories_form.html"
    success_url = reverse_lazy("admin_dashboard:category_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        # self.send_notification("added")
        messages.success(self.request, "Category added successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to add category.")
        return super().form_invalid(form)

# Update category
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "admin_dashboard/categories/categories_form.html"
    success_url = reverse_lazy("admin_dashboard:category_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        # self.send_notification("updated")
        messages.success(self.request, "Category updated successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update category.")
        return super().form_invalid(form)

# Delete category
class CategoryDeleteView(DeleteView):
    model = Category
    success_url = reverse_lazy("admin_dashboard:category_list")
    template_name = "admin_dashboard/categories/categories_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Category deleted successfully.")
        return super().delete(request, *args, **kwargs)
    
# Add Subcategory
class SubCategoryAddView(CreateView):
    model = SubCategory
    form_class = SubCategoryForm
    template_name = "admin_dashboard/categories/sub_category_form.html"

    def form_valid(self, form):
        category_id = self.kwargs.get("category_id")
        category = get_object_or_404(Category, id=category_id)
        form.instance.category = category
        response = super().form_valid(form)
        messages.success(self.request, "Subcategory added successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to add subcategory.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get("category_id")
        context["category"] = get_object_or_404(Category, id=category_id)
        return context

    def get_success_url(self):
        return reverse_lazy("admin_dashboard:category_detail", kwargs={"pk": self.kwargs.get("category_id")})

# Edit Subcategory
class SubCategoryEditView(UpdateView):
    model = SubCategory
    form_class = SubCategoryForm
    template_name = "admin_dashboard/categories/sub_category_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Subcategory updated successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update subcategory.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the category from the SubCategory instance
        context["category"] = self.object.category
        return context

    def get_success_url(self):
        return reverse_lazy("admin_dashboard:category_detail", kwargs={"pk": self.object.category.id})