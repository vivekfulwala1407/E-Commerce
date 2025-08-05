from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from ..models import Product

@csrf_exempt
def shop_products(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        products = Product.objects.all()
        products_data = [
            {
                'id': str(p.id),
                'name': p.name,
                'price': str(p.price),
                'stock': p.stock,
                'description': p.description
            } for p in products
        ]
        return JsonResponse({'products': products_data})
    return JsonResponse({'error': 'Method not allowed'}, status=405)