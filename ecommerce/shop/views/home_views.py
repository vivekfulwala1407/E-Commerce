from django.http import JsonResponse, HttpRequest

def home(request: HttpRequest) -> JsonResponse:
    return JsonResponse({
        'message': 'Welcome to E-Commerce website',
        'browser_endpoints':{
            'products': '/api/products/',
            'cart': '/api/cart/',
            'admin_panel': '/admin/',
        },
        'secure_endpoints': {
            'add_to_cart': '/api/cart/add/',
            'checkout': '/api/checkout/',
        },
        'status': 'running'
    })

