from django.urls import path
from .views import switch_user

urlpatterns = [
    path("switch-user/", switch_user, name="switch_user"),
]
