from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from ..models import Cart, Order

@csrf_exempt
def checkout(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try:
            user = request.user if request.user.is_authenticated else None
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
                        'error': f'Insufficient stock for {item.product.name}'
                    }, status=400)
                total += item.product.price * item.quantity
            
            order = Order.objects.create(user=user, total=total)

            for item in items:
                item.product.stock -= item.quantity
                item.product.save()
            
            items.delete()
            
            return JsonResponse({
                'message': 'Order placed successfully',
                'order_id': str(order.id),
                'total': str(total)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)