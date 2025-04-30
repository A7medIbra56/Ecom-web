from django.contrib.auth import get_user_model, login
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import redirect

User = get_user_model()

def switch_user(request):
    user_id = request.GET.get("user_id")
    
    if user_id:
        user = User.objects.filter(id=user_id).first()
        if user:
            # Set the backend explicitly
            backend = "django.contrib.auth.backends.ModelBackend"
            
            # Store new user in session
            request.session["switch_user_id"] = user.id
            request.session.modified = True  # Mark session as modified
            
            # Log in the new user
            login(request, user, backend=backend)

            # Force Django to reload request.user
            request._cached_user = user  # Override request's cached user

    return redirect(request.META.get("HTTP_REFERER", "/"))
