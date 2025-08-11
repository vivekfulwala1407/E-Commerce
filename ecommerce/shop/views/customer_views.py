from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from ..models import Cart, Order, OrderItem
import json

def get_authenticated_user(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        token_key = auth_header[7:]
        try:
            token = Token.objects.get(key=token_key)
            return token.user, None
        except Token.DoesNotExist:
            return None, JsonResponse({'error': 'Invalid token'}, status=401)
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            token_key = data.get('token')
            if token_key:
                token = Token.objects.get(key=token_key)
                return token.user, None
        except (json.JSONDecodeError, Token.DoesNotExist):
            pass
    
    return None, JsonResponse({'error': 'Authentication required'}, status=401)

@csrf_exempt
def checkout(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        user, error_response = get_authenticated_user(request)
        if error_response:
            return error_response
            
        try:
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return JsonResponse({'error': 'Cart not found'}, status=404)

            items = cart.items.all()
            if not items:
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            total = 0
            for item in items:
                if item.product.stock < item.quantity:
                    return JsonResponse({
                        'error': f'Insufficient stock for {item.product.name}. Available: {item.product.stock}'
                    }, status=400)
                total += item.product.price * item.quantity

            order = Order.objects.create(user=user, total=total)
            order_items_data = []
            
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                item.product.stock -= item.quantity
                item.product.save()

                order_items_data.append({
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'price': str(item.product.price),
                    'total': str(item.product.price * item.quantity)
                })
            items.delete()
            return JsonResponse({
                'message': 'Order placed successfully',
                'order_id': str(order.id),
                'total': str(total),
                'status': order.status,
                'items': order_items_data,
                'item_count': len(order_items_data)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)