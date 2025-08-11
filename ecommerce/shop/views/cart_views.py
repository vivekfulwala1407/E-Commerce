from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import Product, Cart, CartItem
from typing import cast
import json
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
def add_to_cart(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        user, error_response = get_authenticated_user(request)
        if error_response:
            return error_response
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))

            if not product_id:
                return JsonResponse({'error': 'Product ID is required'}, status=400)

            if quantity <= 0:
                return JsonResponse({'error': 'Quantity must be greater than 0'}, status=400)

            product = get_object_or_404(Product, id=product_id)
            if quantity > product.stock:
                return JsonResponse({
                    'error': f'Insufficient stock. Available: {product.stock}'
                }, status=400)

            cart, created = Cart.objects.get_or_create(user=user)
            
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not item_created:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    return JsonResponse({
                        'error': f'Cannot add {quantity} more. Total would exceed stock. Available: {product.stock}, Current in cart: {cart_item.quantity}'
                    }, status=400)
                cart_item.quantity = new_quantity
                cart_item.save()

            return JsonResponse({
                'message': 'Product added to cart successfully',
                'cart_item_id': str(cart_item.id),
                'product_name': product.name,
                'quantity': cart_item.quantity,
                'total_price': str(product.price * cart_item.quantity)
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def update_cart_item(request: HttpRequest, item_id: uuid.UUID) -> JsonResponse:
    if request.method == 'PUT':
        user, error_response = get_authenticated_user(request)
        if error_response:
            return error_response
            
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity'))

            if quantity <= 0:
                return JsonResponse({'error': 'Quantity must be greater than 0'}, status=400)

            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=user)
            
            if quantity > cart_item.product.stock:
                return JsonResponse({
                    'error': f'Insufficient stock. Available: {cart_item.product.stock}'
                }, status=400)

            cart_item.quantity = quantity
            cart_item.save()

            return JsonResponse({
                'message': 'Cart item updated successfully',
                'cart_item_id': str(cart_item.id),
                'product_name': cart_item.product.name,
                'quantity': cart_item.quantity,
                'total_price': str(cart_item.product.price * cart_item.quantity)
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def view_cart(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        user, error_response = get_authenticated_user(request)
        if error_response:
            return error_response
            
        try:
            try:
                cart = Cart.objects.get(user=user)
            except Cart.DoesNotExist:
                return JsonResponse({
                    'cart_items': [],
                    'total_amount': '0.00',
                    'item_count': 0
                })

            items = cart.items.all()
            cart_data = []
            total_amount = 0

            for item in items:
                item_total = item.product.price * item.quantity
                total_amount += item_total
                cart_data.append({
                    'cart_item_id': str(item.id),
                    'product_id': str(item.product.id),
                    'product_name': item.product.name,
                    'price': str(item.product.price),
                    'quantity': item.quantity,
                    'total': str(item_total)
                })
            return JsonResponse({
                'cart_items': cart_data,
                'total_amount': str(total_amount),
                'item_count': len(cart_data)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)