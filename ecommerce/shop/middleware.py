from django.http import JsonResponse
from rest_framework.authtoken.models import Token
import json

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"Middleware processing: {request.path}")
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token_key = auth_header[7:]
            print(f"Found Bearer token: {token_key[:10]}...")
            try:
                token = Token.objects.get(key=token_key)
                request.user = token.user
                print(f"User authenticated: {request.user.username}") 
            except Token.DoesNotExist:
                print("Token not found in database")
                request.user = None
        
        elif request.method == 'POST' and hasattr(request, 'content_type') and request.content_type == 'application/json':
            try:
                body_unicode = request.body.decode('utf-8')
                body = json.loads(body_unicode)
                token_key = body.get('token')
                if token_key:
                    print(f"Found token in body: {token_key[:10]}...") 
                    token = Token.objects.get(key=token_key)
                    request.user = token.user
                    print(f"User authenticated from body: {request.user.username}")  
            except (json.JSONDecodeError, Token.DoesNotExist, UnicodeDecodeError):
                print("Token in body not valid") 
                pass

        response = self.get_response(request)
        return response

class AdminRoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_paths = [
            '/api/admin/',
        ]
        
        is_admin_path = any(request.path.startswith(path) for path in admin_paths)
        
        if is_admin_path:
            print(f"Admin path detected: {request.path}")
            if not hasattr(request, 'user') or not request.user or not request.user.is_authenticated:
                print("No authenticated user for admin path")
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            if not (request.user.is_staff or request.user.is_superuser):
                print(f"User {request.user.username} is not admin")
                return JsonResponse({'error': 'Admin access required'}, status=403)

        response = self.get_response(request)
        return response