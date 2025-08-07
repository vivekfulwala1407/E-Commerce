from django.http import JsonResponse, HttpRequest
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ..models import Order
from typing import cast
import uuid

def customer_order_history(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        try:
            user = cast(User, request.user)
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
        try:
            order = get_object_or_404(Order, id=order_id)
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            user = cast(User, request.user)
            if not user.is_staff and order.user != user:
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
                'items': order_items,
                'item_count': len(order_items)
            }
            return JsonResponse(order_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)