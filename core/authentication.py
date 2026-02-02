from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # Skip CSRF enforcement for API requests
        pass
    
    def authenticate(self, request):
        # Get the user from the Django session
        user = getattr(request._request, 'user', None)
        
        # Return None if user is not authenticated
        if not user or not user.is_authenticated:
            return None
        
        # Return authenticated user
        return (user, None)
