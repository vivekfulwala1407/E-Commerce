from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from ..models import Cart, Product, CartItem
from django.shortcuts import get_object_or_404
import json
import uuid

@csrf_exempt
def add_to_cart(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        try: 
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = data.get('quantity', 1)
            user = request.user if request.user.is_authenticated else None

            try:
                product_id = uuid.UUID(product_id)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid product ID'}, status=400)
            
            product = get_object_or_404(Product, id=product_id)
            if product.stock < quantity:
                return JsonResponse({'error': 'insufficient stock'}, status=400)
            
            cart, _ = Cart.objects.get_or_create(user=user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, 
                product=product,
                defaults={'quantity': 0}
            )
            
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity
            cart_item.save()

            return JsonResponse({
                'message': 'Item added to cart',
                'cart_item_id': str(cart_item.id),
                'total_quantity': cart_item.quantity
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def update_cart_item(request: HttpRequest, item_id: uuid.UUID) -> JsonResponse:
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity'))
            cart_item = get_object_or_404(CartItem, id=item_id)
            
            if quantity <= 0:
                cart_item.delete()
                return JsonResponse({'message': 'Item removed from cart'})
            
            if cart_item.product.stock < quantity:
                return JsonResponse({'error': 'Insufficient stock'}, status=400)

            cart_item.quantity = quantity
            cart_item.save()
            return JsonResponse({
                'message': 'Cart updated',
                'new_quantity': cart_item.quantity,
                'new_total': str(cart_item.product.price * cart_item.quantity)
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def view_cart(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        try:
            user = request.user if request.user.is_authenticated else None
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return JsonResponse({'cart': [], 'total': '0.00'})
            
            items = cart.items.all()
            cart_data = []
            total = 0
            
            for item in items:
                item_total = item.product.price * item.quantity
                total += item_total
                cart_data.append({
                    'id': str(item.id),
                    'product_id': str(item.product.id),
                    'product': item.product.name,
                    'quantity': item.quantity,
                    'price': str(item.product.price),
                    'total': str(item_total)
                })
            
            return JsonResponse({
                'cart': cart_data,
                'total': str(total),
                'item_count': len(cart_data)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)