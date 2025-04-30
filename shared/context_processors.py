from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

def user_list(request):
    return {
        "users": User.objects.all(),
        'current_year': datetime.now().year,
        }