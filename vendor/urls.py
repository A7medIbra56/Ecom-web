from django.contrib.auth import views as auth_views
from django.urls import path
from vendor import views

app_name = "vendor_dashboard"

urlpatterns = [
    
    path('', views.general.home, name='dashboard'),
    
    path("products/", views.product.ProductsListView.as_view(), name="products_list"),
    path("product/create/", views.product.product_create_view, name="product_create"),
    path("product/<int:pk>/", views.product.ProductDetailView.as_view(), name="product_detail"),
    path("product/<int:pk>/edit/", views.product.product_update_view, name="product_update"),
    path("product/<int:pk>/delete/", views.product.ProductDeleteView.as_view(), name="product_delete"),
    
    path("orders/", views.orders.OrdersListView.as_view(), name="orders_list"),
    path("order/<int:pk>/", views.orders.order_detail_view, name="order_detail"),
]