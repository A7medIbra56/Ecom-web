from django.urls import path, include
from ecommerce.users.views import *
from django.views.generic.base import RedirectView
from ecommerce.users.views.account import AccountSupportTicketsList

urlpatterns = [       
    
    # Redirects
    path("login/", RedirectView.as_view(url="/account/login/", permanent=True), name='login'),
    path("signup/", RedirectView.as_view(url="/account/signup/", permanent=True), name='user_signup'),
    path("logout/", RedirectView.as_view(url="/account/logout/", permanent=True), name='logout'),
    
    # Authentication & Account Pages    
    path('account/', include('allauth.urls')),
    path('account/', account.AccountProfileView.as_view(), name='account_home'),
    path('account/edit/', account.AccountProfileEditView.as_view(), name='account_profile_edit'),
    path('account/addresses/', account.AccountAddressListView.as_view(), name='account_addresses'),
    path('account/addresses/add/', account.AccountAddressCreateView.as_view(), name='account_address_create'),
    path('account/addresses/<int:pk>/edit/', account.AccountAddressEditView.as_view(), name='account_address_edit'),
    # path('account/addresses/<int:pk>/delete/', account.AccountAddressDeleteView.as_view(), name='account_address_delete'),
    
    path('account/orders/', account.account_orders, name='account_orders'),
    path('account/support/', AccountSupportTicketsList.as_view(), name='account_support'),
]