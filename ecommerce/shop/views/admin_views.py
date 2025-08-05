from django.http import JsonResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from ..models import Product

@csrf_exempt
def admin_add_product(request: HttpRequest) -> JsonResponse:
    if request.method == 'POST':
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
    if request.method == 'POST':
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
                })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except (ValueError, TypeError) as e:
            return JsonResponse({'error': f'Invalid data: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
