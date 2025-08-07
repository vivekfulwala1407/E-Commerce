from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from ..models import Order
from typing import cast
import json
import uuid

def admin_customer_orders(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        user = cast(User, request.user)
        if user.is_staff:
            return JsonResponse({'error': 'Admin access required'}, status=403)
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

@csrf_exempt
def admin_update_order_status(request: HttpRequest, order_id: uuid.UUID) -> JsonResponse:
    if request.method == 'PUT':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        user = cast(User, request.user)
        if user.is_staff:
            return JsonResponse({'error': 'Admin access required'}, status=403)
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
                'new_status': new_status
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)