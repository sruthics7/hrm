# middleware.py
from django.http import HttpResponseForbidden
from django.conf import settings

class IPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ips = getattr(settings, 'ALLOWED_IPS', [])

    def __call__(self, request):
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Print IP to console for any login attempt
        if request.path.startswith('/login/'):
            print(f"🌐 Login attempt from IP: {ip}")
        
        # Check if trying to access login or admin
        if request.path.startswith('/admin/') or request.path.startswith('/login/'):
            if ip not in self.allowed_ips:
                return HttpResponseForbidden(f"Access denied from IP: {ip}")
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
        