from django.utils import translation
from django.conf import settings
from django.core.management import call_command
from django.utils.cache import patch_cache_control
from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from django.http import HttpResponsePermanentRedirect
import re
import sqlite3

class CacheUpdateMiddleware(MiddlewareMixin):
    def __call__(self, request):
        # Only cache GET requests
        if request.method != 'GET':
            print("Method not get")
            return self.get_response(request)

        print("Method Get")
        # If not in cache or cache needs update, get new response
        print("")
        cache_status, version_key, version_value = self.reset_cache_check()
        print("")
            
        if cache_status:
            call_command("clear_cache")
            cache.set("latest_cache_index", version_value)
            
            if 'cache_reset' not in request.GET:
                redirect_url = request.get_full_path() + ('&' if '?' in request.get_full_path() else '?') + 'cache_reset=true'
                return HttpResponseRedirect(redirect_url)
        
        response = self.get_response(request)
        
        if request.GET.get('cache_reset') == 'true':
            patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True, max_age=0)
            
        return response

    def reset_cache_check(self):
        """
        Checks if the cache version stored in the database is different from the cache version
        stored in the user's session. If different, the cache is considered outdated and needs
        to be updated.
        """
        try:
            conn = sqlite3.connect('db.sqlite3')
            cursor = conn.cursor()

            # Fetch the current content_update_index from the database
            cursor.execute('SELECT content_update_index FROM update_index')
            cache_version = cursor.fetchone()[0]
            conn.close()

            # Check if the user has cached data and a cache_index stored
            cache_key = f"latest_cache_index"
            session_cache_version = cache.get(cache_key)
            
            print(f"Current cache version: {session_cache_version}")
            print(f"Database version: {cache_version}")

            if session_cache_version is None or session_cache_version != cache_version:
                print("Cache version mismatch - triggering reset")
                return True, "latest_cache_index", cache_version
            
            else:
                print("Cache version match - no reset needed")
                return False, '', ''

        except Exception as e:
            print(f"Error checking cache version: {str(e)}")
            return False, '', ''

class URLLanguageConfigMiddleware:
    """
    Middleware to handle language switching based on the URL structure.
    Only triggers if the user manually changes the language code in the URL.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        
        # if path.startswith("/__reload__/"):
        #     return self.get_response(request)

        # Check if the path contains a language code
        url_lang_match = re.match(r'^/admin/([a-z]{2})(/.*)?$', path)
    
        current_lang = translation.get_language()
        
        # Non-Default Language Activate
        if url_lang_match:
            
            url_lang_match = url_lang_match.group(1)
            
            print("Not Default")
            print(url_lang_match)
            print(current_lang)

            # URL Language not changed            
            if current_lang == url_lang_match:
                return self.get_response(request)
            
            # URL Language Changed
            else:    
                if url_lang_match in dict(settings.LANGUAGES).keys():
                    translation.activate(url_lang_match)
                    request.session['preferred_language'] = url_lang_match

                    response = self.get_response(request)
                    
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, url_lang_match)
                    response.set_cookie('X-Reload', 'true')
                    
                    return response
                    
                else:
                    return self.get_response(request)

        # Handle default admin URLs (without language code)
        # elif path.startswith("/admin/"):
        #     if current_lang != settings.DEFAULT_LANGUAGE:
        #         translation.activate(settings.DEFAULT_LANGUAGE)
        #         request.session['preferred_language'] = settings.DEFAULT_LANGUAGE

        #         response = self.get_response(request)
                
        #         response.set_cookie(settings.LANGUAGE_COOKIE_NAME, settings.DEFAULT_LANGUAGE)
        #         response.set_cookie('X-Reload', 'true')

        #         return response
        
        elif path.startswith("/admin/"):
            if current_lang != settings.DEFAULT_LANGUAGE:
                # Ensure the default language is activated without disrupting the admin flow
                translation.activate(settings.DEFAULT_LANGUAGE)
                request.session['preferred_language'] = settings.DEFAULT_LANGUAGE

            return self.get_response(request)

        # Handle regular pages (non-admin URLs)
        else:
            # For regular pages, don't change the URL structure regardless of language
            preferred_lang = request.session.get('preferred_language', settings.DEFAULT_LANGUAGE)

            if current_lang != preferred_lang:
                translation.activate(preferred_lang)

            return self.get_response(request)
        
        # # Default Language Activated
        # else:
        #     print("Default Activated")
        #     print(current_lang)
        #     print(settings.DEFAULT_LANGUAGE)
            
        #     if current_lang != settings.DEFAULT_LANGUAGE:
        #         print("Changing")
        #         translation.activate(settings.DEFAULT_LANGUAGE)
        #         request.session['preferred_language'] = settings.DEFAULT_LANGUAGE

        #         response = self.get_response(request)
                
        #         response.set_cookie(settings.LANGUAGE_COOKIE_NAME, settings.DEFAULT_LANGUAGE)
        #         response.set_cookie('X-Reload', 'true')

        #         return response
                
        #     else:   
        #         return self.get_response(request)
        
class TrailingSlashMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print(f"Processing request: {request.path}")
        # Check if the path does not end with a slash and is not a file
        if not request.path.endswith('/') and not request.path.endswith(('.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.ico')):
            print(f"Trying")
            try:
                # Redirect to the same URL with a trailing slash
                print(f"Redirect: {request.path + '/'}")
                return HttpResponsePermanentRedirect(request.path + '/')
            except Exception:
                # If the URL does not resolve to a view, let the request proceed
                pass
        return None

# For testing purposes to switch between users to test diffrent roles
User = get_user_model()

class UserSwitchMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get("switch_user_id")
        if user_id:
            try:
                request.user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                del request.session["switch_user_id"]
                
                
                
                
                
                
from django.shortcuts import redirect
from django.http import Http404

class DashboardRoutingMiddleware:
    """Middleware to dynamically route dashboard URLs based on user role and approval status."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self.is_dashboard_path(request.path):
            if request.path == "/vendor/":
                return redirect("/vendor/dashboard/")
            
            if request.path == "/admin/":
                return redirect("/admin/dashboard/")
            return self.get_response(request)

        # Ensure user is authenticated and not a customer.
        if not request.user.is_authenticated or request.user.role == 'customer':
            raise Http404("Page not found")

        # For vendor users, enforce approval.
        if request.user.role == 'vendor' and not self.is_vendor_approved(request.user):
            return redirect("vendor_approval_page")
        
        if request.path == '/vendor/':
            return redirect("/vendor/dashboard/")
        
        # Verify that the URL path matches the user's role.
        self.validate_path_for_role(request)

        # If the path is a generic dashboard URL, redirect based on role.
        if request.path.startswith("/dashboard/") or request.path == '/vendor/' or request.path == '/admin/':
            new_path = self.get_redirect_path(request)
            return redirect(new_path)

        return self.get_response(request)

    def is_dashboard_path(self, path):
        """Return True if the request path is dashboard-related."""
        return (
            path.startswith("/dashboard/") or 
            path.startswith("/admin/dashboard/") or 
            path.startswith("/vendor/dashboard/")
        )

    def is_vendor_approved(self, user):
        """Check if a vendor is approved."""
        # Assumes that user.vendor exists if user.role is 'vendor'.
        return getattr(user.vendor, 'is_approved', False)

    def validate_path_for_role(self, request):
        """Raise 404 if the URL does not match the user's role."""
        if request.path.startswith("/admin/dashboard/") and request.user.role != 'admin':
            raise Http404("Page not found")
        if request.path.startswith("/vendor/dashboard/") and request.user.role != 'vendor':
            raise Http404("Page not found")

    def get_redirect_path(self, request):
        """Construct the proper redirect URL based on user role."""
        if request.user.role == "admin":
            return request.path.replace("/dashboard/", "/admin/dashboard/", 1)
        elif request.user.role == "vendor":
            return request.path.replace("/dashboard/", "/vendor/dashboard/", 1)
        else:
            raise Http404("Page not found")