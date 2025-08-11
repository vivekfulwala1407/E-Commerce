from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import Order
from typing import cast
import json
import uuid

def check_admin_access(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token_key = auth_header[7:]
        try:
            token = Token.objects.get(key=token_key)
            user = token.user
            if user.is_staff or user.is_superuser:
                return user, None
            return None, JsonResponse({'error': 'Admin access required'}, status=403)
        except Token.DoesNotExist:
            return None, JsonResponse({'error': 'Invalid token'}, status=401)
    if request.method in ['POST', 'PUT'] and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            token_key = data.get('token')
            if token_key:
                token = Token.objects.get(key=token_key)
                user = token.user
                if user.is_staff or user.is_superuser:
                    return user, None
                return None, JsonResponse({'error': 'Admin access required'}, status=403)
        except (json.JSONDecodeError, Token.DoesNotExist):
            pass
    
    return None, JsonResponse({'error': 'Authentication required'}, status=401)

def admin_customer_orders(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        user, error_response = check_admin_access(request)
        if error_response:
            return error_response
            
        try:
            customer_id = request.GET.get('customer_id')
            status = request.GET.get('status')
            orders_query = Order.objects.all().order_by('-created_at')

            if customer_id:
                try:
                    customer = User.objects.get(pk=customer_id)
                    orders_query = orders_query.filter(user=customer)
                except User.DoesNotExist:
                    return JsonResponse({'error': 'Customer not found'}, status=404)

            if status:
                orders_query = orders_query.filter(status=status)
                
            orders_data = []
            for order in orders_query:
                order_items = []
                for item in order.items.all():
                    order_items.append({
                        'product_id': str(item.product.id),
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'price': str(item.price),
                        'total': str(item.price * item.quantity)
                    })
                orders_data.append({
                    'order_id': str(order.id),
                    'customer_id': order.user.id if order.user else None,
                    'customer_name': order.user.username if order.user else 'Guest',
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

@csrf_exempt
def admin_update_order_status(request: HttpRequest, order_id: uuid.UUID) -> JsonResponse:
    if request.method == 'PUT':
        user, error_response = check_admin_access(request)
        if error_response:
            return error_response
            
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            if not new_status:
                return JsonResponse({'error': 'Status is required'}, status=400)

            valid_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
            if new_status not in valid_statuses:
                return JsonResponse({
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                }, status=400)

            order = get_object_or_404(Order, id=order_id)
            old_status = order.status
            order.status = new_status
            order.save()

            return JsonResponse({
                'message': f'Order status updated from "{old_status}" to "{new_status}"',
                'order_id': str(order.id),
                'old_status': old_status,
                'new_status': new_status
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)