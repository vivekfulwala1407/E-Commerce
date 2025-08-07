from django.urls import path
from .views import home, shop_products, add_to_cart, update_cart_item, view_cart, checkout, admin_add_product, admin_remove_product, admin_modify_product
from .views.auth_views import signup, signin, signout
from .views.pass_views import forgot_password, reset_password, get_user_profile
from .views.orderhistory_views import customer_order_history, order_detail
from .views.handleorder_views import admin_customer_orders, admin_update_order_status

urlpatterns = [
    path('', home, name='home'),  #
    path('api/products/', shop_products, name='shop_products'), #
    path('api/cart/add/', add_to_cart, name='add_to_cart'),  #
    path('api/cart/update/<uuid:item_id>/', update_cart_item, name='update_cart_item'),  #
    path('api/cart/', view_cart, name='view_cart'), #
    path('api/checkout/', checkout, name='checkout'),  #
    path('api/auth/signup/', signup, name='signup'),   #
    path('api/auth/signin/', signin, name='signin'),   #
    path('api/auth/signout/', signout, name='signout'),  #
    path('api/auth/forgot-password/', forgot_password, name='forgot_password'), # 
    path('api/auth/reset-password/<str:uidb64>/<str:token>/', reset_password, name='reset_password'),  #
    path('api/auth/profile/', get_user_profile, name='get_user_profile'),  #
    path('api/orders/', customer_order_history, name='customer_order_history'), #
    path('api/orders/<uuid:order_id>/', order_detail, name='order_detail'),  #
    path('api/admin/product/add/', admin_add_product, name='admin_add_product'),  #
    path('api/admin/product/remove/<uuid:product_id>/', admin_remove_product, name='admin_remove_product'),  #
    path('api/admin/product/modify/<uuid:product_id>/', admin_modify_product, name='admin_modify_product'),  #
    path('api/admin/orders/', admin_customer_orders, name='admin_customer_orders'),   #
    path('api/admin/orders/<uuid:order_id>/status/', admin_update_order_status, name='admin_update_order_status'),
]