"""base URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static

import debug_toolbar
from website import views as website_app_views

urlpatterns = [    
    path('vendor/dashboard/', include('vendor.urls')),
    path('admin/dashboard/', include('admin_dashboard.urls')),
    
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    
    path('captcha/', include('captcha.urls')),
    
    path('django-admin/', admin.site.urls),
    
    path('', include('shared.urls')),
    
    path('', include('website.urls')), 
    
    # path('vendors/', include('ecommerce.vendor.urls')),
    # path('cart/', include('ecommerce.cart.urls')),
    # path('', include('ecommerce.product.urls'))
]

if settings.DEBUG:
    urlpatterns = [
        path('__reload__/', include('django_browser_reload.urls')),
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)