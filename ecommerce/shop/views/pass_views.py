from django.http import JsonResponse, HttpRequest
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from typing import cast
import json

@csrf_exempt
def forgot_password(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({'error': 'Email is required'}, status=400)
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = f"http://localhost:8000/api/auth/reset-password/{uid}/{token}/"

                return JsonResponse({
                    'message': 'Password reset link has been sent',
                    'reset_link': reset_link
                })
            except User.DoesNotExist:
                return JsonResponse({
                    'message': 'Account not exist'
                })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def reset_password(request: HttpRequest, uidb64: str, token: str) -> JsonResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')

            if not new_password or not confirm_password:
                return JsonResponse({'error': 'Both password fields are required'}, status=400)

            if new_password != confirm_password:
                return JsonResponse({'error': 'Passwords do not match'}, status=400)

            if len(new_password) < 8:
                return JsonResponse({'error': 'Password must be at least 8 characters long'}, status=400)

            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)

                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    return JsonResponse({'message': 'Password reset successful'})
                else:
                    return JsonResponse({'error': 'Invalid or expired reset link'}, status=400)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return JsonResponse({'error': 'Invalid reset link'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_user_profile(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = cast(User, request.user)
            return JsonResponse({
                'user_id': user.pk,
                'username': user.username,
                'email': user.email,
            })
        else:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
    return JsonResponse({'error': 'Method not allowed'}, status=405)