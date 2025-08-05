from django.urls import path
from .views import (home, shop_products, add_to_cart, update_cart_item, view_cart, checkout, admin_add_product, admin_remove_product, admin_modify_product)

urlpatterns = [
    path('', home, name='home'),
    path('api/products/', shop_products, name='shop_products'),
    path('api/cart/add/', add_to_cart, name='add_to_cart'),
    path('api/cart/update/<uuid:item_id>/', update_cart_item, name='update_cart_item'),
    path('api/cart/', view_cart, name='view_cart'),
    path('api/checkout/', checkout, name='checkout'),
    path('api/admin/product/add/', admin_add_product, name='admin_add_product'),
    path('api/admin/product/remove/<uuid:product_id>/', admin_remove_product, name='admin_remove_product'),
    path('api/admin/product/modify/<uuid:product_id>/', admin_modify_product, name='admin_modify_product'),
]
