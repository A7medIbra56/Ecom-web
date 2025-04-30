from django.urls import path, include
from website import views
from django.views.generic.base import RedirectView
from vendor import views as vendor_views


urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),

    # User-Vendor Pages
    path('vendor/apply/', vendor_views.general.vendor_apply, name='vendor_apply_page'),
    path('vendor/approval/', vendor_views.general.approval_view, name='vendor_approval_page'),
    
    # Authentication URL's (Login, Signup, Logout, etc) & User Account Pages
    path('', include('ecommerce.users.urls')),
    path('', include('ecommerce.cart.urls')),
    path('', include('ecommerce.product.urls', namespace='products')),
    
    path('email_test/', views.test_base_template, name='email_test'),
    
    # path('notifications/', include('notifications.urls', namespace='notifications')),
]