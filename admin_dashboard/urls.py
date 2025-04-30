from django.urls import path
from admin_dashboard.views import *

app_name = "admin_dashboard"

urlpatterns = [
    path('', general.home, name="home"),
    
    path("vendors/", vendors.VendorListView.as_view(), name="vendor_list"),
    path("vendors/approve/", vendors.ApproveVendorListView.as_view(), name="vendor_approve_list"),
    path("vendor/<int:pk>/", vendors.VendorDetailView.as_view(), name="vendor_detail"),
    path("vendor/<int:pk>/approve/", vendors.VendorApproveView.as_view(), name="vendor_approve"),
    path("vendor/<int:pk>/edit/", vendors.VendorUpdateView.as_view(), name="vendor_update"),
    path("vendor/<int:pk>/delete/", vendors.VendorDeleteView.as_view(), name="vendor_delete"),

    path("products/", products.ProductListView.as_view(), name="product_list"),
    path("products/approve/", products.ApproveProductListView.as_view(), name="product_approve_list"),
    path("product/<int:pk>/", products.ProductDetailView.as_view(), name="product_detail"),
    path("product/<int:pk>/approve/", products.ProductApproveView.as_view(), name="product_approve"),
    path("product/<int:pk>/edit/", products.ProductUpdateView.as_view(), name="product_update"),
    path("product/<int:pk>/delete/", products.ProductDeleteView.as_view(), name="product_delete"),

    path("categories/", categories.CategoryListView.as_view(), name="category_list"),
    path("category/<int:pk>/", categories.CategoryDetailView.as_view(), name="category_detail"),
    path("category/add/", categories.CategoryAddView.as_view(), name="category_add"),
    path("category/<int:pk>/edit/", categories.CategoryUpdateView.as_view(), name="category_edit"),
    path("category/<int:pk>/delete/", categories.CategoryDeleteView.as_view(), name="category_delete"),
    path("category/<int:category_id>/subcategory/add/", categories.SubCategoryAddView.as_view(), name="subcategory_add"),
    path("category/subcategory/<int:pk>/edit/", categories.SubCategoryEditView.as_view(), name="subcategory_edit"),
    
    path("earnings/", earnings.earnings_home, name="earnings_home"),
    path("earnings/transactions/", earnings.TransactionListView.as_view(), name="earnings_transaction_list"),
    path("earnings/transactions/<int:pk>/", earnings.TransactionDetailView.as_view(), name="earnings_transaction_detail"),
    path("earnings/payouts/", earnings.PayoutListView.as_view(), name="earnings_payout_list"),
    path("earnings/payouts/<int:pk>/", earnings.PayoutDetailView.as_view(), name="earnings_payout_detail"),
    
    path("support/", support.SupportTicketListView.as_view(), name="support_list"),
    path("support/ticket/<int:pk>/", support.SupportTicketDetailView.as_view(), name="ticket_detail"),
]
