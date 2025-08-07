from django.http import JsonResponse, HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from typing import cast
import json
import re

@csrf_exempt
def signup(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            required_fields = ['username', 'email', 'password', 'confirm_password']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            username = data['username']
            email = data['email']
            password = data['password']
            confirm_password = data['confirm_password']

            if password != confirm_password:
                return JsonResponse({'error': 'Passwords do not match'}, status=400)

            if len(password) < 8:
                return JsonResponse({'error': 'Password must be at least 8 characters long'}, status=400)

            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                return JsonResponse({'error': 'Invalid email format'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            return JsonResponse({
                'message': 'Account created successfully',
                'user_id': user.pk,
                'username': user.username
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def signin(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    authenticated_user = cast(User, user)
                    return JsonResponse({
                        'message': 'Login successful',
                        'user_id': authenticated_user.pk,
                        'username': authenticated_user.username,
                        'email': authenticated_user.email,
                        'is_staff': authenticated_user.is_staff
                    })
                else:
                    return JsonResponse({'error': 'Account is disabled'}, status=400)
            else:
                return JsonResponse({'error': 'Invalid username or password'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def signout(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try:
            if request.user.is_authenticated:
                user = cast(User, request.user)
                username = user.username
                logout(request)
                return JsonResponse({'message': 'Logged out successfully'})
            else:
                return JsonResponse({'error': 'No user is currently logged in'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)