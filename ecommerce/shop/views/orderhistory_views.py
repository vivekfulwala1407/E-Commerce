from django.http import JsonResponse, HttpRequest
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from ..models import Order
from typing import cast
import uuid

def get_authenticated_user(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token_key = auth_header[7:]
        try:
            token = Token.objects.get(key=token_key)
            return token.user, None
        except Token.DoesNotExist:
            return None, JsonResponse({'error': 'Invalid token'}, status=401)
    if request.method == 'GET':
        token_key = request.GET.get('token')
        if token_key:
            try:
                token = Token.objects.get(key=token_key)
                return token.user, None
            except Token.DoesNotExist:
                pass
    
    return None, JsonResponse({'error': 'Authentication required'}, status=401)

def customer_order_history(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        user, error_response = get_authenticated_user(request)
        if error_response:
            return error_response
            
        try:
            orders = Order.objects.filter(user=user).order_by('-created_at')
            orders_data = []
            
            for order in orders:
                order_items = []
                for item in order.items.all():
                    order_items.append({
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'price': str(item.price),
                        'total': str(item.price * item.quantity)
                    })
                    
                orders_data.append({
                    'order_id': str(order.id),
                    'total': str(order.total),
                    'status': order.status,
                    'created_at': order.created_at.isoformat(),
                    'items': order_items,
                    'item_count': len(order_items)
                })
                
            return JsonResponse({
                'orders': orders_data,
                'total_orders': len(orders_data)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def order_detail(request: HttpRequest, order_id: uuid.UUID) -> JsonResponse:
    if request.method == 'GET':
        user, error_response = get_authenticated_user(request)
        if error_response:
            return error_response
        try:
            order = get_object_or_404(Order, id=order_id)
            if not user or (not (user.is_staff or user.is_superuser) and order.user != user):
                return JsonResponse({'error': 'Permission denied'}, status=403)

            order_items = []
            for item in order.items.all():
                order_items.append({
                    'product_id': str(item.product.id),
                    'product_name': item.product.name,
                    'product_description': item.product.description,
                    'quantity': item.quantity,
                    'price': str(item.price),
                    'total': str(item.price * item.quantity)
                })
                
            order_data = {
                'order_id': str(order.id),
                'customer': {
                    'customer_id': order.user.id if order.user else None,
                    'username': order.user.username if order.user else 'Guest',
                },
                'total': str(order.total),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'items': order_items,
                'item_count': len(order_items)
            }
            return JsonResponse(order_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)