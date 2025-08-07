from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from ..models import Cart, Order, OrderItem

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