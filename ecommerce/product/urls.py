from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path('search/', views.search, name='search'),
    path('<slug:category_slug>/<slug:product_slug>/', views.product, name='product'),
]