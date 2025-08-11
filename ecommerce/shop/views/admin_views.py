from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
import json
import uuid
from ..models import Product

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

@csrf_exempt
def admin_add_product(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
        user, error_response = check_admin_access(request)
        if error_response:
            return error_response
            
        try:
            data = json.loads(request.body)
            required_fields = ['name', 'price', 'stock']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            product = Product.objects.create(
                name=data.get('name'),
                price=float(data.get('price')),
                stock=int(data.get('stock')),
                description=data.get('description', '')
            )
            return JsonResponse({
                'message': 'Product added successfully',
                'product_id': str(product.id),
                'product_name': product.name
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except (ValueError, TypeError) as e:
            return JsonResponse({'error': f'Invalid data: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def admin_remove_product(request: HttpRequest, product_id: uuid.UUID) -> JsonResponse:
    if request.method == 'DELETE':
        user, error_response = check_admin_access(request)
        if error_response:
            return error_response
            
        try:
            product = get_object_or_404(Product, id=product_id)
            product_name = product.name
            product.delete()
            return JsonResponse({
                'message': f'Product "{product_name}" removed successfully'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def admin_modify_product(request: HttpRequest, product_id: uuid.UUID) -> JsonResponse:
    if request.method == 'PUT':
        user, error_response = check_admin_access(request)
        if error_response:
            return error_response
            
        try:
            data = json.loads(request.body)
            product = get_object_or_404(Product, id=product_id)
            
            if 'name' in data:
                product.name = data['name']
            if 'price' in data:
                product.price = float(data['price'])
            if 'stock' in data:
                product.stock = int(data['stock'])
            if 'description' in data:
                product.description = data['description']
            
            product.save()

            return JsonResponse({
                'message': 'Product updated successfully',
                'product_id': str(product.id),
                'product_name': product.name
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except (ValueError, TypeError) as e:
            return JsonResponse({'error': f'Invalid data: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)